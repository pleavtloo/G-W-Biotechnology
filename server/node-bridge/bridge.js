/**
 * Run server/worker.js on Node — for hosts that cannot reach *.workers.dev.
 *
 * The worker module is unchanged; this file only supplies the two things Node
 * does not have natively:
 *   env.LEAD_KV / env.COA_INDEX  -> in-process Map with TTL support
 *   ctx.waitUntil                -> immediate promise (fire and forget)
 *
 * Deploy: see README.md in this folder.
 */
import { createHash, createHmac, randomBytes, scryptSync, timingSafeEqual, webcrypto } from "node:crypto";
import { appendFile, readFile, readdir, stat } from "node:fs/promises";
import { execSync } from "node:child_process";
import http from "node:http";

import oauth from "../oauth-worker/worker.js";
import worker from "../worker.js";

// Node 18 has no global WebCrypto; the worker uses crypto.subtle for the IP hash.
if (!globalThis.crypto) {
  globalThis.crypto = webcrypto;
}

/* --- mail: send through local SMTP instead of the Resend API ---
 * worker.js posts to https://api.resend.com/emails; this host cannot use a
 * third-party mail API, so those calls are redirected to smtp_send.py which
 * talks SMTP with an authenticated mailbox. worker.js stays untouched.
 * Set RESEND_API_KEY to any non-empty value so the worker attempts the send.
 */
const realFetch = globalThis.fetch.bind(globalThis);
const SMTP_SIDECAR = process.env.SMTP_SIDECAR || "http://127.0.0.1:8082/send";

globalThis.fetch = async (url, init) => {
  const target = typeof url === "string" ? url : (url && url.url) || "";
  if (target.indexOf("api.resend.com") === -1) {
    return realFetch(url, init);
  }
  let payload = {};
  try {
    payload = JSON.parse((init && init.body) || "{}");
  } catch {
    payload = {};
  }
  const to = Array.isArray(payload.to) ? payload.to : [payload.to].filter(Boolean);
  return realFetch(SMTP_SIDECAR, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      from: payload.from,
      to,
      subject: payload.subject,
      text: payload.text,
      reply_to: payload.reply_to,
    }),
  });
};

const PORT = Number(process.env.PORT || 8081);

/* --- minimal KV stand-in: get / put with expirationTtl --- */
const store = new Map();
const KV = {
  async get(key, type) {
    const item = store.get(String(key));
    if (!item) return null;
    if (item.exp && Date.now() > item.exp) {
      store.delete(String(key));
      return null;
    }
    // the worker asks for "json" when reading rate-limit counters
    if (type === "json") {
      try {
        return JSON.parse(item.value);
      } catch {
        return null;
      }
    }
    return item.value;
  },
  async put(key, value, opts) {
    store.set(String(key), {
      value,
      exp: opts && opts.expirationTtl ? Date.now() + opts.expirationTtl * 1000 : 0,
    });
  },
  async delete(key) {
    store.delete(String(key));
  },
};

const env = {
  ENVIRONMENT: process.env.ENVIRONMENT || "staging",
  LEAD_FROM: process.env.LEAD_FROM || "site@gwbioth.com",
  LEAD_TO: process.env.LEAD_TO || "",
  LEAD_REPLY_TO: process.env.LEAD_REPLY_TO || "",
  RECEIPT_SIGNER: process.env.RECEIPT_SIGNER || "",
  RESEND_API_KEY: process.env.RESEND_API_KEY || "",
  TURNSTILE_SECRET: process.env.TURNSTILE_SECRET || "",
  CRM_WEBHOOK: process.env.CRM_WEBHOOK || "",
  IP_SALT: process.env.IP_SALT || "",
  LEAD_KV: KV,
  COA_INDEX: KV,
  // the CMS login bridge, mounted at /oauth/* on this same origin
  GITHUB_CLIENT_ID: process.env.GITHUB_CLIENT_ID || "",
  GITHUB_CLIENT_SECRET: process.env.GITHUB_CLIENT_SECRET || "",
  STATE_SECRET: process.env.STATE_SECRET || "",
  OAUTH_PREFIX: "/oauth",
};

function readBody(req) {
  return new Promise((resolve) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks)));
  });
}

/* ---------------- pageview analytics (cookie-free, same origin) ---------------- */

const HITS_FILE = process.env.HITS_FILE || "/opt/tl-api/hits.jsonl";
const STATUS_FILE = process.env.STATUS_FILE || "/opt/tl-api/deploy-status.json";
const ORDERS_FILE = process.env.ORDERS_FILE || "/opt/tl-api/orders.jsonl";
const ORDERS_TOKEN = process.env.ORDERS_TOKEN || "";
const SKIP_PREFIX = ["/admin", "/stats", "/api", "/oauth"];

/* ---------------- customer accounts ----------------
 * Same JSONL approach as orders. Passwords use scrypt with a per-user salt;
 * a session id lives in an HttpOnly cookie so page scripts cannot read it.
 */

const USERS_FILE = process.env.USERS_FILE || "/opt/tl-api/users.jsonl";
const SESSIONS_FILE = process.env.SESSIONS_FILE || "/opt/tl-api/sessions.jsonl";
const CONTENT_API = process.env.CONTENT_API || "http://127.0.0.1:8084";
const CONTENT_KEY = process.env.CONTENT_KEY || "";

/* ---------------- Stripe (REST, no SDK on this box) ----------------
 * Card data is entered on checkout.stripe.com, never here: that keeps the site
 * out of PCI scope and means we only ever see a session id.
 */
const STRIPE_SK = process.env.STRIPE_SECRET_KEY || "";
const PUBLIC_URL = (process.env.PUBLIC_URL || "").replace(/\/$/, "");

async function stripePost(path, params) {
  const body = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") {
      body.append(key, String(value));
    }
  }
  const r = await realFetch("https://api.stripe.com/v1/" + path, {
    method: "POST",
    headers: {
      authorization: "Bearer " + STRIPE_SK,
      "content-type": "application/x-www-form-urlencoded",
    },
    body: body.toString(),
  });
  const data = await r.json();
  if (!r.ok) {
    throw new Error((data.error && data.error.message) || "stripe " + r.status);
  }
  return data;
}

async function stripeGet(path) {
  const r = await realFetch("https://api.stripe.com/v1/" + path, {
    headers: { authorization: "Bearer " + STRIPE_SK },
  });
  const data = await r.json();
  if (!r.ok) {
    throw new Error((data.error && data.error.message) || "stripe " + r.status);
  }
  return data;
}

/**
 * What the admin panel shows about the payment account. The key itself never
 * leaves the server; only its mode and prefix do. Cached for five minutes so
 * opening the System tab does not hit Stripe every time.
 */
let stripeCache = { at: 0, value: null };

async function stripeStatus() {
  const sk = process.env.STRIPE_SECRET_KEY || "";
  const wh = process.env.STRIPE_WEBHOOK_SECRET || "";
  const base = {
    mode: sk.startsWith("sk_live_") ? "live" : sk.startsWith("sk_test_") ? "test" : "none",
    key_prefix: sk ? sk.slice(0, 12) + "…" : "",
    webhook: wh ? "configured" : "missing",
    reachable: null,
  };
  if (!sk) return base;
  if (stripeCache.value && Date.now() - stripeCache.at < 300000) return stripeCache.value;

  const out = { ...base };
  try {
    const r = await realFetch("https://api.stripe.com/v1/account", {
      headers: { authorization: "Bearer " + sk },
    });
    out.reachable = r.ok;
    if (r.ok) {
      const a = await r.json();
      out.account = a.id;
      out.country = a.country;
      out.currency = a.default_currency;
      out.charges = a.charges_enabled;
      out.payouts = a.payouts_enabled;
      out.details = a.details_submitted;
      out.business = (a.business_profile || {}).name || "";
    }
  } catch {
    out.reachable = false;
  }
  stripeCache = { at: Date.now(), value: out };
  return out;
}

/**
 * Stripe signs "timestamp.payload" with the endpoint secret. Anything older than
 * five minutes is refused so a captured request cannot be replayed later.
 */
function verifyStripeSig(raw, header, secret) {
  if (!header || !secret) return false;
  const parts = {};
  for (const chunk of String(header).split(",")) {
    const i = chunk.indexOf("=");
    if (i > 0) parts[chunk.slice(0, i).trim()] = chunk.slice(i + 1).trim();
  }
  const stamp = Number(parts.t || 0);
  const given = parts.v1 || "";
  if (!stamp || !given) return false;
  if (Math.abs(Date.now() / 1000 - stamp) > 300) return false;

  const expected = createHmac("sha256", secret).update(stamp + "." + raw).digest("hex");
  const a = Buffer.from(expected, "utf8");
  const b = Buffer.from(given, "utf8");
  if (a.length !== b.length) return false;
  return timingSafeEqual(a, b);
}

async function createCheckoutSession(order) {
  // payment_method_types is no longer accepted: Stripe manages the enabled
  // methods from the dashboard now.
  const params = {
    mode: "payment",
    client_reference_id: order.id,
    "metadata[order_id]": order.id,
    success_url: PUBLIC_URL + "/checkout.html?session_id={CHECKOUT_SESSION_ID}",
    cancel_url: PUBLIC_URL + "/checkout.html?cancelled=1",
    customer_email: order.fields.work_email,
  };

  order.items.forEach((it, i) => {
    const unit = Math.round((Number(it.price) || 0) * 100);
    params["line_items[" + i + "][quantity]"] = Number(it.qty) || 1;
    params["line_items[" + i + "][price_data][currency]"] = "usd";
    params["line_items[" + i + "][price_data][unit_amount]"] = unit;
    params["line_items[" + i + "][price_data][product_data][name]"] =
      (it.name || "Item") + " — " + (it.spec || "");
    params["line_items[" + i + "][price_data][product_data][metadata][sku]"] = it.sku || "";
  });

  return stripePost("checkout/sessions", params);
}
const SESSION_DAYS = 30;
const PASSWORD_MIN = 8;

function scryptHash(password) {
  const salt = randomBytes(16).toString("hex");
  const hash = scryptSync(String(password), salt, 64).toString("hex");
  return "scrypt$" + salt + "$" + hash;
}

function scryptVerify(password, stored) {
  const parts = String(stored || "").split("$");
  if (parts.length !== 3 || parts[0] !== "scrypt") return false;
  const candidate = scryptSync(String(password), parts[1], 64);
  const expected = Buffer.from(parts[2], "hex");
  return candidate.length === expected.length && timingSafeEqual(candidate, expected);
}

function parseCookies(req) {
  const raw = String(req.headers["cookie"] || "");
  const out = {};
  for (const part of raw.split(";")) {
    const idx = part.indexOf("=");
    if (idx > 0) out[part.slice(0, idx).trim()] = decodeURIComponent(part.slice(idx + 1).trim());
  }
  return out;
}

function sessionCookie(sid, maxAge) {
  const secure = (process.env.PUBLIC_HTTPS || "1") === "1" ? "; Secure" : "";
  return "tl_session=" + sid + "; HttpOnly; SameSite=Lax; Path=/; Max-Age=" +
    maxAge + secure;
}

async function readUsers() {
  let text = "";
  try {
    text = await readFile(USERS_FILE, "utf8");
  } catch {
    return [];
  }
  const map = new Map();
  for (const line of text.split("\n")) {
    if (!line) continue;
    let rec;
    try {
      rec = JSON.parse(line);
    } catch {
      continue;
    }
    if (rec.type === "user" && rec.id) map.set(rec.id, rec);
    else if (rec.type === "user_update" && map.has(rec.id)) {
      Object.assign(map.get(rec.id), rec.patch || {});
    }
  }
  return Array.from(map.values());
}

async function currentUser(req) {
  const sid = parseCookies(req).tl_session;
  if (!sid) return null;
  let text = "";
  try {
    text = await readFile(SESSIONS_FILE, "utf8");
  } catch {
    return null;
  }
  let found = null;
  for (const line of text.split("\n")) {
    if (!line) continue;
    let rec;
    try {
      rec = JSON.parse(line);
    } catch {
      continue;
    }
    if (rec.type === "session" && rec.sid === sid) found = rec;
    if (rec.type === "logout" && rec.sid === sid) found = null;
  }
  if (!found || found.exp < Date.now()) return null;
  const users = await readUsers();
  return users.find((u) => u.id === found.user) || null;
}

function publicUser(u) {
  if (!u) return null;
  return {
    id: u.id, email: u.email, name: u.name, company: u.company,
    status: u.status, role: u.role || "customer", created: u.created,
  };
}

async function handleRegister(rawBody, req, res) {
  let d = {};
  try {
    d = JSON.parse(rawBody.toString("utf8") || "{}");
  } catch {
    d = {};
  }
  const email = String(d.email || "").trim().toLowerCase();
  const password = String(d.password || "");
  const name = String(d.name || "").trim().slice(0, 80);
  const company = String(d.company || "").trim().slice(0, 120);

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return jsonOut(res, { ok: false, error: "Enter a valid email address." }, 400);
  }
  if (password.length < PASSWORD_MIN) {
    return jsonOut(res, { ok: false, error: "Password must be at least " + PASSWORD_MIN + " characters." }, 400);
  }
  if (!name || !company) {
    return jsonOut(res, { ok: false, error: "Name and organisation are required." }, 400);
  }

  const users = await readUsers();
  if (users.some((u) => u.email === email)) {
    return jsonOut(res, { ok: false, error: "That email already has an account." }, 409);
  }

  const user = {
    t: Date.now(), type: "user",
    id: "U-" + Date.now().toString(36).toUpperCase() +
        Math.random().toString(36).slice(2, 5).toUpperCase(),
    email: email, name: name, company: company,
    pw: scryptHash(password),
    status: "pending",              // pending -> active after a human approves
    role: "customer",
    created: Date.now(),
  };
  try {
    await appendFile(USERS_FILE, JSON.stringify(user) + "\n");
  } catch {
    return jsonOut(res, { ok: false, error: "Could not save the account." }, 500);
  }

  await sendMailDirect({
    to: process.env.LEAD_TO || "info@gwbioth.com",
    subject: "[account] New registration — " + company,
    text: "New customer account waiting for approval.\n\n" +
      "Name:    " + name + "\nCompany: " + company + "\nEmail:   " + email + "\n\n" +
      "Approve or reject it at /orders.html (Users tab).",
  });
  await sendMailDirect({
    to: email,
    subject: "We received your G&W Biotechnologie GmbH account request",
    text: "Hello " + name + ",\n\n" +
      "Thanks for registering. We review new accounts individually so we can price and ship " +
      "correctly. You will hear from us within one business day (Mon–Fri).\n\n" +
      "G&W Biotechnologie GmbH\n" +
      "To Life. From Discovery to Therapy",
  });

  return jsonOut(res, { ok: true, user: publicUser(user) });
}

async function handleLogin(rawBody, req, res) {
  let d = {};
  try {
    d = JSON.parse(rawBody.toString("utf8") || "{}");
  } catch {
    d = {};
  }
  const email = String(d.email || "").trim().toLowerCase();
  const password = String(d.password || "");
  const users = await readUsers();
  const user = users.find((u) => u.email === email);

  if (!user || !scryptVerify(password, user.pw)) {
    return jsonOut(res, { ok: false, error: "Email or password is incorrect." }, 401);
  }
  if (user.status === "rejected") {
    return jsonOut(res, { ok: false, error: "This account was not approved. Contact us." }, 403);
  }

  const sid = randomBytes(32).toString("hex");
  const exp = Date.now() + SESSION_DAYS * 86400000;
  try {
    await appendFile(SESSIONS_FILE, JSON.stringify({
      t: Date.now(), type: "session", sid: sid, user: user.id, exp: exp,
    }) + "\n");
  } catch {
    return jsonOut(res, { ok: false, error: "Could not start a session." }, 500);
  }

  res.setHeader("set-cookie", sessionCookie(sid, SESSION_DAYS * 86400));
  return jsonOut(res, { ok: true, user: publicUser(user) });
}

/* ---------------- password reset ----------------
 * The token is random, stored only as a SHA-256 hash, valid for an hour and
 * single-use. The forgot endpoint always answers the same way so it cannot be
 * used to discover which addresses have accounts.
 */
const RESET_FILE = process.env.RESET_FILE || "/opt/tl-api/resets.jsonl";
const RESET_TTL = 3600 * 1000;
const forgotHits = new Map();

async function handleForgot(rawBody, req, res) {
  let d = {};
  try {
    d = JSON.parse(rawBody.toString("utf8") || "{}");
  } catch {
    d = {};
  }
  const email = String(d.email || "").trim().toLowerCase();
  const generic = {
    ok: true,
    message: "If that address has an account, a reset link is on its way. It expires in one hour.",
  };

  const ip = clientIp(req);
  const now = Date.now();
  const recent = (forgotHits.get(ip) || []).filter((t) => now - t < 3600000);
  if (recent.length >= 3) {
    return jsonOut(res, { ok: false, error: "Too many requests. Try again in an hour." }, 429);
  }
  forgotHits.set(ip, recent.concat(now));

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return jsonOut(res, generic);

  const users = await readUsers();
  const user = users.find((u) => u.email === email);
  if (!user) return jsonOut(res, generic);

  const token = randomBytes(32).toString("hex");
  const hash = createHash("sha256").update(token).digest("hex");
  try {
    await appendFile(RESET_FILE, JSON.stringify({
      t: now, type: "reset", hash: hash, user: user.id, exp: now + RESET_TTL,
    }) + "\n");
  } catch {
    return jsonOut(res, generic);
  }

  const link = PUBLIC_URL + "/reset.html?token=" + token;
  sendMailDirect({
    to: email,
    subject: "Reset your G&W Biotechnologie GmbH password",
    text: "Hello " + (user.name || "there") + ",\n\n" +
      "Use the link below to set a new password. It works once and expires in one hour.\n\n" +
      link + "\n\n" +
      "If you did not ask for this, ignore this email — your password stays as it is.\n\n" +
      "G&W Biotechnologie GmbH\n" +
      "To Life. From Discovery to Therapy",
  }).catch(() => {});

  return jsonOut(res, generic);
}

async function handleReset(rawBody, req, res) {
  let d = {};
  try {
    d = JSON.parse(rawBody.toString("utf8") || "{}");
  } catch {
    d = {};
  }
  const token = String(d.token || "");
  const password = String(d.password || "");

  if (!/^[a-f0-9]{64}$/.test(token)) {
    return jsonOut(res, { ok: false, error: "That link is not valid. Ask for a new one." }, 400);
  }
  if (password.length < PASSWORD_MIN) {
    return jsonOut(res, { ok: false, error: "Password must be at least " + PASSWORD_MIN + " characters." }, 400);
  }

  const hash = createHash("sha256").update(token).digest("hex");
  let text = "";
  try {
    text = await readFile(RESET_FILE, "utf8");
  } catch {
    text = "";
  }

  let record = null;
  const spent = new Set();
  for (const line of text.split("\n")) {
    if (!line) continue;
    let rec;
    try {
      rec = JSON.parse(line);
    } catch {
      continue;
    }
    if (rec.type === "used" && rec.hash) spent.add(rec.hash);
    if (rec.type === "reset" && rec.hash === hash) record = rec;
  }

  if (!record || record.exp < Date.now() || spent.has(hash)) {
    return jsonOut(res, { ok: false, error: "That link has expired or was already used." }, 400);
  }

  try {
    await appendFile(USERS_FILE, JSON.stringify({
      t: Date.now(), type: "user_update", id: record.user, patch: { pw: scryptHash(password) },
    }) + "\n");
    await appendFile(RESET_FILE, JSON.stringify({ t: Date.now(), type: "used", hash: hash }) + "\n");
  } catch {
    return jsonOut(res, { ok: false, error: "Could not save the new password." }, 500);
  }

  return jsonOut(res, { ok: true });
}

async function handleLogout(req, res) {
  const sid = parseCookies(req).tl_session;
  if (sid) {
    try {
      await appendFile(SESSIONS_FILE, JSON.stringify({
        t: Date.now(), type: "logout", sid: sid,
      }) + "\n");
    } catch {
      /* cookie is cleared anyway */
    }
  }
  res.setHeader("set-cookie", sessionCookie("", 0));
  return jsonOut(res, { ok: true });
}

/* ---------------- orders (append-only JSONL, no database needed) ----------------
 * Each order is one line. Status changes are appended as separate lines, so the
 * file is never rewritten: a crash mid-write can at most lose the last line.
 */

function newOrderId() {
  const d = new Date();
  const stamp = d.toISOString().slice(0, 10).replace(/-/g, "");
  const rand = Math.random().toString(36).slice(2, 6).toUpperCase();
  return "TL-" + stamp + "-" + rand;
}

async function readOrders() {
  let text = "";
  try {
    text = await readFile(ORDERS_FILE, "utf8");
  } catch {
    return [];
  }
  const map = new Map();
  for (const line of text.split("\n")) {
    if (!line) continue;
    let rec;
    try {
      rec = JSON.parse(line);
    } catch {
      continue;
    }
    if (rec.type === "order" && rec.id) {
      map.set(rec.id, Object.assign({ status: "new", history: [] }, rec));
    } else if (rec.type === "status" && map.has(rec.id)) {
      const o = map.get(rec.id);
      o.status = rec.status;
      o.history.push({ at: rec.t, status: rec.status });
    }
  }
  return Array.from(map.values()).sort((a, b) => b.t - a.t);
}

async function sendMailDirect({ to, subject, text }) {
  const target = process.env.SMTP_SIDECAR || "http://127.0.0.1:8082/send";
  try {
    const r = await realFetch(target, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        from: process.env.LEAD_FROM || "G&W Biotechnologie GmbH <noreply@gwbioth.com>",
        to: Array.isArray(to) ? to : [to],
        subject: subject,
        text: text,
      }),
    });
    return r.ok;
  } catch {
    return false;
  }
}

function ordersAuthed(req) {
  return Boolean(ORDERS_TOKEN) &&
    String(req.headers["authorization"] || "") === "Bearer " + ORDERS_TOKEN;
}

async function bankDetails() {
  try {
    const r = await realFetch(CONTENT_API + "/content/site", {
      headers: { "x-content-key": CONTENT_KEY },
    });
    const d = await r.json();
    return (d && d.data && d.data.bank) || {};
  } catch {
    return {};
  }
}

function bankBlock(bank) {
  const lines = [];
  if (bank.beneficiary) lines.push("  Beneficiary:  " + bank.beneficiary);
  if (bank.account) lines.push("  Account:      " + bank.account);
  if (bank.swift) lines.push("  SWIFT / BIC:  " + bank.swift);
  if (bank.bank_name) lines.push("  Bank:         " + bank.bank_name);
  if (bank.bank_address) lines.push("  Bank address: " + bank.bank_address);
  if (bank.terms) lines.push("  Terms:        " + bank.terms);
  return lines.length ? lines.join("\n") : "  We will send the bank details in a separate email.";
}

async function createOrder(rawBody, req, res) {
  let data = {};
  try {
    data = JSON.parse(rawBody.toString("utf8") || "{}");
  } catch {
    data = {};
  }
  const f = data.fields || {};
  const items = Array.isArray(data.items) ? data.items : [];
  if (!items.length) {
    return jsonOut(res, { ok: false, error: "Your cart is empty — add a pack size first." }, 400);
  }
  if (!f.work_email) {
    return jsonOut(res, { ok: false, error: "A work email is required." }, 400);
  }
  // Checked here too: the browser can be bypassed and Stripe rejects bad
  // addresses, which would silently drop the payment link.
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(String(f.work_email))) {
    return jsonOut(res, { ok: false, error: "Please enter a valid work email address." }, 400);
  }

  // Orders are account-only: browsing stays open, committing to buy does not.
  const me = await currentUser(req);
  if (!me) {
    return jsonOut(res, {
      ok: false, needLogin: true,
      error: "Please sign in to place an order.",
    }, 401);
  }
  if ((me.status || "pending") !== "active") {
    return jsonOut(res, {
      ok: false, needApproval: true,
      error: "Your account is awaiting approval. We usually reply within one business day.",
    }, 403);
  }

  const payment = data.payment === "bank_transfer" ? "bank_transfer" : "online";
  const id = newOrderId();
  const total = items.reduce(
    (n, it) => n + (Number(it.price) || 0) * (Number(it.qty) || 0), 0);

  try {
    await appendFile(ORDERS_FILE, JSON.stringify({
      t: Date.now(), type: "order", id: id, fields: f, items: items,
      total: total, payment: payment, user: me ? me.id : null, ip: clientIp(req),
    }) + "\n");
  } catch (err) {
    console.error("order write failed:", err && err.message);
    return jsonOut(res, { ok: false, error: "could not save order" }, 500);
  }

  // Card orders: create the Stripe session before composing the emails, so the
  // confirmation can carry the link and the browser can go straight there.
  let session = null;
  if (payment === "online" && STRIPE_SK) {
    try {
      session = await createCheckoutSession({ id: id, fields: f, items: items });
    } catch (err) {
      console.error("stripe session failed:", err && err.message);
    }
  }

  const lines = items.map((it) =>
    "  " + it.spec + (it.sku ? " (" + it.sku + ")" : "") + " x" + it.qty +
    " = $" + ((Number(it.price) || 0) * (Number(it.qty) || 0))
  ).join("\n");

  const methodLabel = payment === "bank_transfer"
    ? "Bank transfer / purchase order"
    : "Card payment (secure link to follow)";

  const body = [
    "Order request " + id, "",
    "Name:     " + (f.full_name || "-"),
    "Company:  " + (f.organisation || "-"),
    "Email:    " + f.work_email,
    "Phone:    " + (f.phone || "-"),
    "Ship to:  " + [f.address, f.city, f.postcode, f.country].filter(Boolean).join(", "),
    "Payment:  " + methodLabel,
    (f.po_number ? "PO number: " + f.po_number : ""),
    (f.billing_name ? "Invoice to: " + f.billing_name : ""),
    (f.vat_number ? "VAT / tax id: " + f.vat_number : ""),
    "Notes:    " + (f.notes || "-"), "",
    "Items:", lines, "",
    "Subtotal: $" + total, "",
    (payment === "online" && !session
      ? "!! Stripe could not create a payment link for this order. Send one manually.\n"
      : ""),
    "Confirm stock, shipping and lead time, then reply to the customer.",
  ].filter(function (line) { return line !== ""; }).join("\n");

  const bank = payment === "bank_transfer" ? await bankDetails() : {};
  const payBlock = payment === "bank_transfer"
    ? "Payment: bank transfer or purchase order.\n\nBank details:\n" + bankBlock(bank) + "\n\n" +
      "Please quote " + id + " as the payment reference."
    : (session
        ? "Payment: card. Complete it here:\n  " + session.url + "\n\n" +
          "Card details are entered on Stripe's page, not on our site."
        : "Payment: we will email a secure card payment link within one business day (Mon–Fri).\n" +
          "Card details are entered on Stripe's page, not on our site.");

  const mailTo = process.env.LEAD_TO || "info@gwbioth.com";

  // SMTP takes ~10s per message; the customer must not wait for it. The order is
  // already persisted above, so mail failures are logged and nothing is lost.
  sendMailDirect({
    to: mailTo,
    subject: "[order] " + id + " — " + (f.organisation || f.work_email),
    text: body,
  }).then((ok) => {
    if (!ok) console.error("order mail failed:", id);
  }).catch(() => {});

  sendMailDirect({
    to: f.work_email,
    subject: "Order request " + id + " received — G&W Biotechnologie GmbH",
    text: "Hello " + (f.full_name || "there") + ",\n\n" +
      "We received your order request " + id + ".\n\n" +
      lines + "\n\nSubtotal: $" + total + "\n\n" +
      payBlock + "\n\n" +
      "We will confirm availability, shipping cost and lead time within one business day (Mon–Fri). " +
      "No payment has been taken yet.\n\n" +
      "G&W Biotechnologie GmbH\n" +
      "To Life. From Discovery to Therapy",
  }).catch(() => {});

  return jsonOut(res, {
    ok: true, id: id, total: total, mailed: "queued",
    checkoutUrl: session ? session.url : null,
  });
}

function jsonOut(res, obj, status = 200) {
  const body = Buffer.from(JSON.stringify(obj));
  res.writeHead(status, {
    "content-type": "application/json; charset=utf-8",
    "content-length": body.length,
    "cache-control": "no-store",
  });
  res.end(body);
}

function clientIp(req) {
  const raw = req.headers["x-real-ip"] || req.socket.remoteAddress || "";
  return String(raw).replace(/^::ffff:/, "");
}

async function recordHit(rawBody, req, res) {
  let data = {};
  try {
    data = JSON.parse(rawBody.toString("utf8") || "{}");
  } catch {
    data = {};
  }
  const page = String(data.p || "").slice(0, 120);
  if (!page || SKIP_PREFIX.some((p) => page.startsWith(p))) {
    return jsonOut(res, { ok: true, skipped: true });
  }
  // store a salted hash of the address, never the address itself
  const visitor = createHash("sha256").update(clientIp(req) + "|tl").digest("hex").slice(0, 12);
  const line = JSON.stringify({
    t: Date.now(),
    p: page,
    u: visitor,
    r: String(data.r || "").slice(0, 120),
  }) + "\n";
  try {
    await appendFile(HITS_FILE, line);
  } catch (err) {
    console.error("hit write failed:", err && err.message);
  }
  return jsonOut(res, { ok: true });
}

async function sendStats(res, url) {
  const days = Math.min(90, Math.max(1, Number(url.searchParams.get("days")) || 7));
  const since = Date.now() - days * 86400000;
  let text = "";
  try {
    text = await readFile(HITS_FILE, "utf8");
  } catch {
    text = "";
  }

  const byDay = new Map();
  const byPage = new Map();
  const visitors = new Set();
  let pv = 0;

  for (const line of text.split("\n")) {
    if (!line) continue;
    let hit;
    try {
      hit = JSON.parse(line);
    } catch {
      continue;
    }
    if (!hit || hit.t < since) continue;
    pv += 1;
    visitors.add(hit.u);
    const day = new Date(hit.t).toISOString().slice(0, 10);
    byDay.set(day, (byDay.get(day) || 0) + 1);
    const entry = byPage.get(hit.p) || { pv: 0, uv: new Set() };
    entry.pv += 1;
    entry.uv.add(hit.u);
    byPage.set(hit.p, entry);
  }

  const series = [];
  for (let i = days - 1; i >= 0; i -= 1) {
    const day = new Date(Date.now() - i * 86400000).toISOString().slice(0, 10);
    series.push({ d: day, pv: byDay.get(day) || 0 });
  }

  const pages = Array.from(byPage.entries())
    .map(([p, v]) => ({ p, pv: v.pv, uv: v.uv.size }))
    .sort((a, b) => b.pv - a.pv)
    .slice(0, 20);

  return jsonOut(res, { ok: true, days, total: { pv, uv: visitors.size }, series, pages });
}

function toHeaders(req) {
  const headers = new Headers();
  for (const [name, value] of Object.entries(req.headers)) {
    if (typeof value === "string") headers.set(name, value);
  }
  // nginx sets X-Real-IP; the worker hashes cf-connecting-ip for rate limiting
  const ip = req.headers["x-real-ip"] || (req.socket.remoteAddress || "");
  headers.set("cf-connecting-ip", String(ip).replace(/^::ffff:/, ""));
  return headers;
}

const server = http.createServer(async (req, res) => {
  try {
    const hasBody = !(req.method === "GET" || req.method === "HEAD");
    const body = hasBody ? await readBody(req) : undefined;

    // Build the request with the origin the browser used (nginx forwards both),
    // because the OAuth bridge derives redirect_uri from it.
    const proto = req.headers["x-forwarded-proto"] || "http";
    const host = req.headers["host"] || `127.0.0.1:${PORT}`;
    const base = `${proto}://${host}`;

    // analytics endpoints live here, before the worker's four routes
    const pathOnly = req.url.split("?")[0];
    if (pathOnly === "/api/hit" && req.method === "POST") {
      return await recordHit(body, req, res);
    }
    if (pathOnly === "/api/stats") {
      return await sendStats(res, new URL(req.url, base));
    }
    if (pathOnly === "/api/deploy-status") {
      try {
        const raw = await readFile(STATUS_FILE, "utf8");
        res.writeHead(200, {
          "content-type": "application/json; charset=utf-8",
          "cache-control": "no-store",
        });
        return void res.end(raw);
      } catch {
        return jsonOut(res, { state: "unknown" });
      }
    }

    if (pathOnly === "/api/register" && req.method === "POST") {
      return await handleRegister(body, req, res);
    }
    if (pathOnly === "/api/login" && req.method === "POST") {
      return await handleLogin(body, req, res);
    }
    if (pathOnly === "/api/logout" && req.method === "POST") {
      return await handleLogout(req, res);
    }
    if (pathOnly === "/api/forgot" && req.method === "POST") {
      return await handleForgot(body, req, res);
    }
    if (pathOnly === "/api/reset" && req.method === "POST") {
      return await handleReset(body, req, res);
    }
    if (pathOnly === "/api/me") {
      const me = await currentUser(req);
      return jsonOut(res, { ok: true, user: publicUser(me) });
    }
    if (pathOnly === "/api/password" && req.method === "POST") {
      const me = await currentUser(req);
      if (!me) return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      let d = {};
      try {
        d = JSON.parse(body.toString("utf8") || "{}");
      } catch {
        d = {};
      }
      const oldPw = String(d.current || "");
      const newPw = String(d.next || "");
      if (!scryptVerify(oldPw, me.pw)) {
        return jsonOut(res, { ok: false, error: "Current password is incorrect." }, 400);
      }
      if (newPw.length < PASSWORD_MIN) {
        return jsonOut(res, { ok: false, error: "New password must be at least " + PASSWORD_MIN + " characters." }, 400);
      }
      try {
        await appendFile(USERS_FILE, JSON.stringify({
          t: Date.now(), type: "user_update", id: me.id,
          patch: { pw: scryptHash(newPw) },
        }) + "\n");
      } catch {
        return jsonOut(res, { ok: false, error: "Could not save the password." }, 500);
      }
      return jsonOut(res, { ok: true });
    }

    // Admin surface: everything under /api/admin is proxied to the YAML sidecar
    // after a role check here, so the content process never faces the network.
    if (pathOnly.startsWith("/api/admin/")) {
      const me = await currentUser(req);
      if (!me || (me.role || "customer") !== "admin") {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }
      const sub = pathOnly.slice("/api/admin/".length);
      const query = req.url.indexOf("?") > -1 ? req.url.slice(req.url.indexOf("?")) : "";
      try {
        const upstream = await realFetch(CONTENT_API + "/" + sub + query, {
          method: req.method,
          headers: { "content-type": "application/json", "x-content-key": CONTENT_KEY },
          body: hasBody ? body : undefined,
        });
        const text = await upstream.text();
        res.writeHead(upstream.status, {
          "content-type": "application/json; charset=utf-8",
          "cache-control": "no-store",
        });
        return void res.end(text);
      } catch (err) {
        return jsonOut(res, { ok: false, error: "content service unavailable" }, 503);
      }
    }
    if (pathOnly === "/api/users" && req.method === "GET") {
      // Accept either the ops token or a signed-in admin session.
      const sessionUser = await currentUser(req);
      const sessionAdmin = sessionUser && (sessionUser.role || "customer") === "admin";
      if (!ordersAuthed(req) && !sessionAdmin) {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }
      const list = (await readUsers()).map(publicUser);
      return jsonOut(res, { ok: true, users: list });
    }
    if (pathOnly === "/api/users/status" && req.method === "POST") {
      const sUser = await currentUser(req);
      const sAdmin = sUser && (sUser.role || "customer") === "admin";
      if (!ordersAuthed(req) && !sAdmin) {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }
      let patch = {};
      try {
        patch = JSON.parse(body.toString("utf8") || "{}");
      } catch {
        patch = {};
      }
      if (!patch.id || ["pending", "active", "rejected"].indexOf(patch.status) === -1) {
        return jsonOut(res, { ok: false, error: "missing id or bad status" }, 400);
      }
      try {
        await appendFile(USERS_FILE, JSON.stringify({
          t: Date.now(), type: "user_update", id: String(patch.id),
          patch: { status: patch.status },
        }) + "\n");
      } catch {
        return jsonOut(res, { ok: false, error: "could not save" }, 500);
      }
      return jsonOut(res, { ok: true });
    }

    // GET /api/order/<id> — one order, visible to its owner or an admin.
    if (pathOnly.startsWith("/api/order/") && req.method === "GET") {
      const wanted = decodeURIComponent(pathOnly.slice("/api/order/".length));
      if (wanted === "verify") return jsonOut(res, { ok: false, error: "method not allowed" }, 405);
      const viewer = await currentUser(req);
      if (!viewer) return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      const all = await readOrders();
      const order = all.find((o) => o.id === wanted);
      if (!order) return jsonOut(res, { ok: false, error: "not found" }, 404);
      const isAdmin = (viewer.role || "customer") === "admin";
      const ownerEmail = String((order.fields || {}).work_email || "").toLowerCase();
      const isOwner = (order.user && order.user === viewer.id) ||
        (!order.user && ownerEmail === viewer.email);
      if (!isAdmin && !isOwner) {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }
      return jsonOut(res, { ok: true, order: order });
    }

    if (pathOnly.startsWith("/api/invoice/") && req.method === "GET") {
      const invoiceId = decodeURIComponent(pathOnly.slice("/api/invoice/".length));
      const viewer = await currentUser(req);
      const all = await readOrders();
      const order = all.find((o) => o.id === invoiceId);
      if (!order) return jsonOut(res, { ok: false, error: "not found" }, 404);

      const isAdmin = viewer && (viewer.role || "customer") === "admin";
      const ownerEmail = String((order.fields || {}).work_email || "").toLowerCase();
      const isOwner = viewer && (
        (order.user && order.user === viewer.id) || (!order.user && ownerEmail === viewer.email));
      if (!isAdmin && !isOwner) {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }

      try {
        const upstream = await realFetch(CONTENT_API + "/invoice", {
          method: "POST",
          headers: { "content-type": "application/json", "x-content-key": CONTENT_KEY },
          body: JSON.stringify({ order: order }),
        });
        if (!upstream.ok) {
          return jsonOut(res, { ok: false, error: "could not render the invoice" }, 502);
        }
        const buffer = Buffer.from(await upstream.arrayBuffer());
        res.writeHead(200, {
          "content-type": "application/pdf",
          "content-length": buffer.length,
          "content-disposition": 'inline; filename="' + invoiceId + '.pdf"',
          "cache-control": "no-store",
        });
        return void res.end(buffer);
      } catch (err) {
        console.error("invoice failed:", err && err.message);
        return jsonOut(res, { ok: false, error: "could not render the invoice" }, 502);
      }
    }

    // Stripe calls this directly: no session, the signature is the credential.
    if (pathOnly === "/api/stripe-webhook" && req.method === "POST") {
      const whsec = process.env.STRIPE_WEBHOOK_SECRET || "";
      const raw = body.toString("utf8");
      const sig = String(req.headers["stripe-signature"] || "");

      if (!whsec) {
        console.error("stripe webhook: STRIPE_WEBHOOK_SECRET is not set");
        return jsonOut(res, { ok: false, error: "not configured" }, 400);
      }
      if (!verifyStripeSig(raw, sig, whsec)) {
        console.error("stripe webhook: signature rejected");
        return jsonOut(res, { ok: false, error: "bad signature" }, 400);
      }

      let event = {};
      try {
        event = JSON.parse(raw);
      } catch {
        return jsonOut(res, { ok: true, ignored: "unparsable" });
      }

      const obj = (event.data && event.data.object) || {};
      const oid = (obj.metadata && obj.metadata.order_id) || obj.client_reference_id || "";

      if (event.type === "checkout.session.completed" &&
          obj.payment_status === "paid" && oid) {
        const all = await readOrders();
        const order = all.find((o) => o.id === oid);
        if (!order) {
          console.error("stripe webhook: unknown order", oid);
          return jsonOut(res, { ok: true, ignored: "unknown order" });
        }
        // Stripe retries until it gets a 2xx, so this must be idempotent.
        if (order.status === "paid" || order.status === "shipped") {
          return jsonOut(res, { ok: true, already: true });
        }

        try {
          await appendFile(ORDERS_FILE, JSON.stringify({
            t: Date.now(), type: "status", id: oid, status: "paid",
            meta: { session: obj.id, amount: obj.amount_total, via: "webhook" },
          }) + "\n");
        } catch {
          return jsonOut(res, { ok: false, error: "could not save" }, 500);
        }

        const f = order.fields || {};
        const amount = "$" + ((Number(obj.amount_total) || 0) / 100).toFixed(2);

        if (f.work_email) {
          sendMailDirect({
            to: f.work_email,
            subject: "Payment received for " + oid,
            text: "Hello " + (f.full_name || "there") + ",\n\n" +
              "We have received your card payment of " + amount + " for order " + oid + ".\n\n" +
              "We will confirm stock and dispatch within one business day (Mon\u2013Fri).\n" +
              "Stripe has emailed your receipt.\n\n" +
              "G&W Biotechnologie GmbH\n" +
      "To Life. From Discovery to Therapy",
          }).catch(() => {});
        }
        sendMailDirect({
          to: process.env.LEAD_TO || "info@gwbioth.com",
          subject: "[paid] " + oid + " \u2014 " + amount,
          text: "Order " + oid + " was paid by card.\n\n" +
            "Customer: " + (f.organisation || f.work_email || "") + "\n" +
            "Amount:   " + amount + "\n" +
            "Stripe:   " + obj.id + "\n\n" +
            "Confirm stock and dispatch.",
        }).catch(() => {});

        return jsonOut(res, { ok: true, paid: oid });
      }

      return jsonOut(res, { ok: true, ignored: event.type || "unknown" });
    }

    if (pathOnly === "/api/order/verify" && req.method === "POST") {
      let d = {};
      try {
        d = JSON.parse(body.toString("utf8") || "{}");
      } catch {
        d = {};
      }
      const sid = String(d.session_id || "");
      if (!STRIPE_SK) return jsonOut(res, { ok: false, error: "card payments are not configured" }, 400);
      if (!/^cs_[A-Za-z0-9_]+$/.test(sid)) {
        return jsonOut(res, { ok: false, error: "bad session id" }, 400);
      }
      try {
        const session = await stripeGet("checkout/sessions/" + encodeURIComponent(sid));
        const paid = session.payment_status === "paid";
        const oid = (session.metadata && session.metadata.order_id) || session.client_reference_id || "";
        if (paid && oid) {
          await appendFile(ORDERS_FILE, JSON.stringify({
            t: Date.now(), type: "status", id: oid, status: "paid",
            meta: { session: sid, amount: session.amount_total },
          }) + "\n");
        }
        return jsonOut(res, {
          ok: true, paid: paid, id: oid,
          amount: session.amount_total, email: session.customer_email || "",
        });
      } catch (err) {
        console.error("stripe verify failed:", err && err.message);
        return jsonOut(res, { ok: false, error: "could not verify the payment" }, 502);
      }
    }

    if (pathOnly === "/api/order" && req.method === "POST") {
      return await createOrder(body, req, res);
    }
    // Health of the box: last backups, services, disk. Admin only.
    if (pathOnly === "/api/system" && req.method === "GET") {
      const sysUser = await currentUser(req);
      if (!sysUser || (sysUser.role || "customer") !== "admin") {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }

      let backup = {};
      try {
        backup = JSON.parse(await readFile("/opt/tl-api/backup-status.json", "utf8"));
      } catch {
        backup = { ok: false, note: "no backup status yet" };
      }

      let files = [];
      try {
        const names = (await readdir("/opt/backups"))
          .filter((n) => /^tl-backup-.*\.tar\.gz$/.test(n)).sort();
        const recent = names.slice(-3).reverse();
        files = [];
        for (const name of recent) {
          const info = await stat("/opt/backups/" + name);
          files.push({ name, size: info.size, at: info.mtime.toISOString() });
        }
      } catch {
        files = [];
      }

      let disk = "";
      try {
        disk = execSync("df -h / | tail -1", { timeout: 4000, encoding: "utf8" }).trim();
      } catch {
        disk = "";
      }

      const services = {};
      for (const svc of ["tl-api", "tl-content", "tl-mail"]) {
        try {
          services[svc] = execSync("systemctl is-active " + svc,
            { timeout: 4000, encoding: "utf8" }).trim();
        } catch {
          services[svc] = "unknown";
        }
      }

      let deploy = {};
      try {
        deploy = JSON.parse(await readFile(STATUS_FILE, "utf8"));
      } catch {
        deploy = {};
      }

      return jsonOut(res, {
        ok: true, backup, files, disk, services, deploy,
        stripe: await stripeStatus(),
      });
    }

    // Admin edits to an account: profile fields, status, or a password reset.
    if (pathOnly === "/api/users/update" && req.method === "POST") {
      const updUser = await currentUser(req);
      const updAdmin = updUser && (updUser.role || "customer") === "admin";
      if (!ordersAuthed(req) && !updAdmin) {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }
      let d = {};
      try {
        d = JSON.parse(body.toString("utf8") || "{}");
      } catch {
        d = {};
      }
      const targetId = String(d.id || "");
      if (!targetId) return jsonOut(res, { ok: false, error: "missing id" }, 400);

      const patch = {};
      ["name", "company"].forEach(function (k) {
        if (typeof d[k] === "string") patch[k] = d[k].trim().slice(0, 160);
      });
      if (typeof d.email === "string") {
        const mail = d.email.trim().toLowerCase();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(mail)) {
          return jsonOut(res, { ok: false, error: "Enter a valid email address." }, 400);
        }
        const users = await readUsers();
        if (users.some(function (u) { return u.email === mail && u.id !== targetId; })) {
          return jsonOut(res, { ok: false, error: "That email already belongs to another account." }, 409);
        }
        patch.email = mail;
      }
      if (["pending", "active", "rejected"].indexOf(d.status) > -1) patch.status = d.status;

      // Optional password set in the same call.
      if (typeof d.password === "string" && d.password.length) {
        if (d.password.length < PASSWORD_MIN) {
          return jsonOut(res, {
            ok: false, error: "Password must be at least " + PASSWORD_MIN + " characters.",
          }, 400);
        }
        patch.pw = scryptHash(d.password);
      }

      if (!Object.keys(patch).length) {
        return jsonOut(res, { ok: false, error: "Nothing to update." }, 400);
      }
      try {
        await appendFile(USERS_FILE, JSON.stringify({
          t: Date.now(), type: "user_update", id: targetId, patch: patch,
        }) + "\n");
      } catch {
        return jsonOut(res, { ok: false, error: "Could not save." }, 500);
      }
      return jsonOut(res, { ok: true, changed: Object.keys(patch) });
    }

    if (pathOnly === "/api/my-orders" && req.method === "GET") {
      const me = await currentUser(req);
      if (!me) return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      const all = await readOrders();
      const mine = all.filter((o) =>
        (o.user && o.user === me.id) ||
        (!o.user && ((o.fields || {}).work_email || "").toLowerCase() === me.email));
      return jsonOut(res, { ok: true, user: publicUser(me), orders: mine });
    }
    if (pathOnly === "/api/orders" && req.method === "GET") {
      const oUser = await currentUser(req);
      const oAdmin = oUser && (oUser.role || "customer") === "admin";
      if (!ordersAuthed(req) && !oAdmin) {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }
      const list = await readOrders();
      return jsonOut(res, { ok: true, orders: list });
    }
    if (pathOnly === "/api/orders/status" && req.method === "POST") {
      const osUser = await currentUser(req);
      const osAdmin = osUser && (osUser.role || "customer") === "admin";
      if (!ordersAuthed(req) && !osAdmin) {
        return jsonOut(res, { ok: false, error: "unauthorized" }, 401);
      }
      let patch = {};
      try {
        patch = JSON.parse(body.toString("utf8") || "{}");
      } catch {
        patch = {};
      }
      if (!patch.id || !patch.status) {
        return jsonOut(res, { ok: false, error: "missing id or status" }, 400);
      }
      const newStatus = String(patch.status).slice(0, 20);
      try {
        await appendFile(ORDERS_FILE, JSON.stringify({
          t: Date.now(), type: "status", id: String(patch.id), status: newStatus,
        }) + "\n");
      } catch {
        return jsonOut(res, { ok: false, error: "could not save" }, 500);
      }

      // Tell the customer, unless the caller opts out or the status says nothing
      // useful to them.
      const NOTES = {
        confirmed: ["Order %%ID%% confirmed", "We have confirmed your order %%ID%% and started preparing it."],
        paid: ["Payment received for %%ID%%", "We have received your payment for order %%ID%%. Thank you."],
        shipped: ["Order %%ID%% has shipped", "Your order %%ID%% is on its way."],
        cancelled: ["Order %%ID%% cancelled", "Order %%ID%% has been cancelled. If this is unexpected, reply to this email."],
      };
      const note = NOTES[newStatus];
      if (note && patch.notify !== false) {
        (async () => {
          const all = await readOrders();
          const target = all.find((o) => o.id === String(patch.id));
          const email = target && target.fields && target.fields.work_email;
          if (!email) return;
          await sendMailDirect({
            to: email,
            subject: note[0].replace(/%%ID%%/g, String(patch.id)),
            text: "Hello " + ((target.fields.full_name) || "there") + ",\n\n" +
              note[1].replace(/%%ID%%/g, String(patch.id)) + "\n\n" +
              "G&W Biotechnologie GmbH\n" +
      "To Life. From Discovery to Therapy",
          });
        })().catch(() => {});
      }

      return jsonOut(res, { ok: true, notified: Boolean(note) && patch.notify !== false });
    }

    const isOauth = req.url.startsWith("/oauth/");
    const target = new URL(isOauth ? req.url.replace(/^\/oauth/, "") : req.url, base);

    const request = new Request(target, {
      method: req.method,
      headers: toHeaders(req),
      body,
    });

    const handler = isOauth ? oauth : worker;
    const response = await handler.fetch(request, env, { waitUntil: () => {} });
    const headers = {};
    response.headers.forEach((value, name) => {
      headers[name] = value;
    });
    res.writeHead(response.status, headers);
    res.end(Buffer.from(await response.arrayBuffer()));
  } catch (err) {
    console.error("bridge error:", err && err.message);
    res.writeHead(500, { "content-type": "application/json" });
    res.end(JSON.stringify({ ok: false, error: "bridge_error" }));
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log("tl-api bridge listening on 127.0.0.1:" + PORT +
    " env=" + env.ENVIRONMENT + " mail=" + Boolean(env.RESEND_API_KEY) +
    " leadTo=" + Boolean(env.LEAD_TO));
});
