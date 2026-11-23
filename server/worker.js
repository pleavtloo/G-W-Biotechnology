/**
 * G&W Biotechnologie GmbH — edge API
 *
 * Routes
 *   POST /api/lead    quote requests, partner applications, CTA subscriptions
 *   POST /api/coa     lot number lookup -> document URL
 *   POST /api/chat    AI assistant (P1: retrieval Q&A) — stub until the index is ready
 *   GET  /api/health
 *
 * Bindings / env
 *   ENVIRONMENT        "production" enables the fail-closed config check below
 *   RESEND_API_KEY     transactional email (https://resend.com)
 *   LEAD_TO            comma separated recipients, e.g. "sales@x.com,qa@x.com"
 *   LEAD_FROM          verified sender, e.g. "site@gwbioth.com"
 *   LEAD_REPLY_TO      reply-to for the visitor receipt; defaults to the first LEAD_TO
 *   RECEIPT_SIGNER     human signatory for the receipt, e.g. "Jane Doe, Applications Lead"
 *   TURNSTILE_SECRET   required in production; when set, `turnstileToken` is required
 *   CRM_WEBHOOK        optional POST target for a flat CRM record (2s timeout)
 *   LEAD_KV            KV namespace: rate-limit counters (rl:*) + failed mails (failed:*)
 *   IP_SALT            optional pepper for the IP hash used in rate-limit keys
 *   COA_INDEX          KV namespace: lot number -> { file, sku, released }
 *   COA_BASE           public base URL for COA files, e.g. https://files.example.com/coa/
 *   CHAT_API_URL       upstream LLM / RAG endpoint (OpenAI-compatible chat completions)
 *   CHAT_API_KEY       bearer token for the above
 *
 * Design notes
 *   - Every route fails closed and returns JSON, never HTML.
 *   - The form endpoint never echoes user input back (no reflected XSS surface).
 *   - Requests are capped at 16 KB and 12 fields; anything larger is dropped.
 *   - Rate-limit keys hold a salted IP hash, never the raw address.
 *   - Logs carry event names, field names and lengths; never the submission body.
 */

const MAX_BODY = 16 * 1024;
const MAX_FIELDS = 12;

const RL_WINDOW = 300;         // seconds
const RL_MAX = 5;              // submissions per window per endpoint
const MAIL_TIMEOUT = 5000;     // ms, per attempt
const CRM_TIMEOUT = 2000;      // ms
const MAIL_BACKOFF = [0, 300, 900];  // first try + 2 retries
const FAILED_TTL = 7 * 24 * 3600;    // 7 days

const json = (body, status = 200, headers = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
      ...headers,
    },
  });

const bad = (msg, status = 400) => json({ ok: false, error: msg }, status);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* ------------------------------------------------------------------ utils */

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

async function readJson(req) {
  const len = Number(req.headers.get("content-length") || 0);
  if (len > MAX_BODY) return { error: "payload too large" };
  const text = await req.text();
  if (text.length > MAX_BODY) return { error: "payload too large" };
  try {
    return { data: JSON.parse(text) };
  } catch {
    return { error: "invalid json" };
  }
}

function cleanFields(fields) {
  const out = {};
  let n = 0;
  for (const [k, v] of Object.entries(fields || {})) {
    if (n++ >= MAX_FIELDS) break;
    if (typeof v !== "string") continue;
    const key = k.replace(/[^a-z0-9_ -]/gi, "").slice(0, 40);
    const val = v.replace(/\s+/g, " ").trim().slice(0, 2000);
    if (key && val) out[key] = val;
  }
  return out;
}

function pickEmail(fields) {
  for (const [k, v] of Object.entries(fields)) {
    if (/e-?mail/i.test(k) && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) return v;
  }
  const any = Object.values(fields).find((v) => /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v));
  return any || "";
}

/** Salted SHA-256 of the client address, first 16 hex chars. Never store the raw IP. */
async function hashIp(ip, salt) {
  const input = new TextEncoder().encode(`${ip || "anon"}|${salt || "tl-site"}`);
  const buf = await crypto.subtle.digest("SHA-256", input);
  return Array.from(new Uint8Array(buf))
    .slice(0, 8)
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/* ------------------------------------------------------- rate limiting */

/**
 * Sliding window over KV.
 *   { allowed: true, off: true }                  — KV not bound, limiter disabled
 *   { allowed: true, remaining: n }
 *   { allowed: false, retryAfter: seconds }
 */
async function rateLimit(env, ipHash, endpoint) {
  if (!env.LEAD_KV) return { allowed: true, off: true };
  const key = `rl:${ipHash}:${endpoint}`;
  const now = Math.floor(Date.now() / 1000);
  let hits = [];
  try {
    const raw = await env.LEAD_KV.get(key, "json");
    if (Array.isArray(raw)) hits = raw.filter((t) => typeof t === "number");
  } catch {
    return { allowed: true, off: true };
  }

  const recent = hits.filter((t) => now - t < RL_WINDOW).sort((a, b) => a - b);
  if (recent.length >= RL_MAX) {
    const oldest = recent[recent.length - RL_MAX];
    return { allowed: false, retryAfter: Math.max(1, RL_WINDOW - (now - oldest)) };
  }

  recent.push(now);
  try {
    await env.LEAD_KV.put(key, JSON.stringify(recent), { expirationTtl: RL_WINDOW });
  } catch {
    // counters are best effort; a KV hiccup must not block a real customer
  }
  return { allowed: true, remaining: RL_MAX - recent.length };
}

/* ------------------------------------------------------------- turnstile */

async function verifyTurnstile(env, token, ip) {
  if (!env.TURNSTILE_SECRET) return { ok: true, off: true };
  if (!token) return { ok: false, reason: "missing token" };
  const body = new FormData();
  body.append("secret", env.TURNSTILE_SECRET);
  body.append("response", token);
  if (ip) body.append("remoteip", ip);
  try {
    const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body,
    });
    const out = await r.json().catch(() => ({}));
    if (out.success === true) return { ok: true };
    const codes = Array.isArray(out["error-codes"]) ? out["error-codes"].join(",") : "failed";
    return { ok: false, reason: codes };
  } catch (e) {
    return { ok: false, reason: `siteverify unreachable: ${String((e && e.message) || e)}` };
  }
}

/* ------------------------------------------------------------------ mail */

async function postResend(env, payload) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), MAIL_TIMEOUT);
  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        authorization: `Bearer ${env.RESEND_API_KEY}`,
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: ctrl.signal,
    });
    if (!r.ok) return { ok: false, error: `mail ${r.status}` };
    const out = await r.json().catch(() => ({}));
    return { ok: true, id: out.id || "" };
  } catch (e) {
    return { ok: false, error: String((e && e.message) || e) };
  } finally {
    clearTimeout(timer);
  }
}

/**
 * Send one email with exponential backoff (1 try + 2 retries).
 * status: "sent" | "failed" | "skipped"
 */
async function sendMail(env, mail) {
  const to = (Array.isArray(mail.to) ? mail.to.join(",") : String(mail.to || ""))
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (!env.RESEND_API_KEY || !to.length) return { status: "skipped" };

  const payload = {
    from: env.LEAD_FROM || "site@gwbioth.com",
    to,
    subject: mail.subject,
    text: mail.text,
  };
  if (mail.replyTo) payload.reply_to = mail.replyTo;

  let last = "";
  for (let i = 0; i < MAIL_BACKOFF.length; i++) {
    if (MAIL_BACKOFF[i]) await sleep(MAIL_BACKOFF[i]);
    const out = await postResend(env, payload);
    if (out.ok) return { status: "sent", attempts: i + 1, id: out.id };
    last = out.error;
  }
  return { status: "failed", attempts: MAIL_BACKOFF.length, error: last };
}

/* ------------------------------------------------------------------- crm */

/** Flat POST to the customer CRM. Never throws, never blocks the response. */
async function crmPush(env, payload) {
  if (!env.CRM_WEBHOOK) return { status: "skip" };
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), CRM_TIMEOUT);
  try {
    const r = await fetch(env.CRM_WEBHOOK, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload),
      signal: ctrl.signal,
    });
    return r.ok ? { status: "ok" } : { status: "err", error: `crm ${r.status}` };
  } catch (e) {
    return { status: "err", error: String((e && e.message) || e) };
  } finally {
    clearTimeout(timer);
  }
}

/* --------------------------------------------------------------- receipts */

// Only these keys are echoed back to the visitor; everything else is ignored.
const RECEIPT_KEYS = [
  "full_name", "name", "organisation", "organization", "company", "country",
  "i_am_interested_in", "interest", "application", "what_are_you_working_on", "message",
];

function receiptLines(fields) {
  const out = [];
  for (const [k, v] of Object.entries(fields)) {
    if (out.length >= 6) break;
    if (/e-?mail/i.test(k)) continue;
    if (RECEIPT_KEYS.indexOf(k) === -1) continue;
    out.push(`  ${k.replace(/_/g, " ")}: ${String(v).slice(0, 200)}`);
  }
  if (!out.length) {
    for (const [k, v] of Object.entries(fields)) {
      if (out.length >= 4) break;
      if (/e-?mail/i.test(k)) continue;
      out.push(`  ${k.replace(/_/g, " ")}: ${String(v).slice(0, 160)}`);
    }
  }
  return out;
}

function receiptText(fields, env) {
  const greeted = fields.full_name || fields.name || "";
  const signer = (env.RECEIPT_SIGNER || "").trim() || "Applications team, G&W Biotechnologie GmbH";
  const lines = receiptLines(fields);
  return [
    greeted ? `Hello ${greeted.split(" ")[0]},` : "Hello,",
    "",
    "Thank you for contacting G&W Biotechnologie GmbH. This is an automatic confirmation that your",
    "enquiry reached our applications team. A named specialist will reply within one business day (Mon–Fri).",
    "",
    "What we received:",
    ...(lines.length ? lines : ["  (no details attached)"]),
    "",
    "This message confirms receipt only. Pricing and lead time are confirmed by the specialist",
    "handling your request, in their reply.",
    "",
    "If anything above is wrong, reply to this email and we will correct it.",
    "",
    signer,
    "G&W Biotechnologie GmbH · Mainz, California",
    "https://www.gwbioth.com/contact.html",
  ].join("\n");
}

/* ------------------------------------------------------------------ helpers */

function logLine(evt, data) {
  console.log(JSON.stringify({ evt, ...data }));
}

function fieldShape(fields) {
  return Object.entries(fields).map(([k, v]) => ({ k, len: v.length }));
}

async function archiveFailure(env, record) {
  if (!env.LEAD_KV) return false;
  try {
    await env.LEAD_KV.put(`failed:${new Date().toISOString()}`, JSON.stringify(record), {
      expirationTtl: FAILED_TTL,
    });
    return true;
  } catch (e) {
    console.error(JSON.stringify({ evt: "lead_archive_err", msg: String((e && e.message) || e) }));
    return false;
  }
}

/* ------------------------------------------------------------------ routes */

async function handleLead(req, env, ctx) {
  const started = Date.now();

  // Fail closed: production without a Turnstile secret would silently accept bots.
  if (env.ENVIRONMENT === "production" && !env.TURNSTILE_SECRET) {
    console.error(JSON.stringify({ evt: "config", ok: false, msg: "TURNSTILE_SECRET missing in production" }));
    return json({ ok: false, error: "verification not configured" }, 503);
  }

  const { data, error } = await readJson(req);
  if (error) return bad(error);

  const raw = data.fields && typeof data.fields === "object" ? data.fields : {};
  if (raw.website_url) return json({ ok: true }); // honeypot: accept, discard

  const fields = cleanFields(raw);
  if (!Object.keys(fields).length) return bad("empty submission");

  const kind = String(data.form || "lead").replace(/[^a-z0-9_-]/gi, "").slice(0, 24) || "lead";
  const page = String(data.path || "").slice(0, 200);

  const ip = req.headers.get("cf-connecting-ip") || "";
  const ipHash = await hashIp(ip, env.IP_SALT);

  const rl = await rateLimit(env, ipHash, "lead");
  if (!rl.allowed) {
    logLine("lead", {
      form: kind, ok: false, reason: "rate_limited", mail: "skip", crm: "skip",
      rl: "hit", ms: Date.now() - started,
    });
    return json(
      { ok: false, error: "rate_limited", retryAfter: rl.retryAfter },
      429,
      { "retry-after": String(rl.retryAfter) }
    );
  }

  const ts = await verifyTurnstile(env, data.turnstileToken, ip);
  if (!ts.ok) {
    logLine("lead", {
      form: kind, ok: false, reason: "verification", ts: ts.reason || "failed",
      mail: "skip", crm: "skip", rl: rl.off ? "off" : "ok", ms: Date.now() - started,
    });
    return bad("verification failed", 403);
  }

  const email = pickEmail(fields);
  if (!email) return bad("a valid email address is required");

  const lines = Object.entries(fields).map(([k, v]) => `${k}: ${v}`);
  const notice = [
    `Form: ${kind}`,
    `Page: ${page}`,
    `Referrer: ${String(data.referrer || "-").slice(0, 200)}`,
    "",
    ...lines,
    "",
    `Received: ${new Date().toISOString()}`,
    `IP: ${ip || "-"}`,
  ].join("\n");

  const mail = await sendMail(env, {
    to: env.LEAD_TO,
    subject: `[site] ${kind} — ${email}`,
    text: notice,
    replyTo: email,
  });

  if (mail.status === "failed") {
    console.error(JSON.stringify({ evt: "lead_mail_failed", form: kind, attempts: mail.attempts, msg: mail.error }));
    await archiveFailure(env, {
      reason: mail.error || "mail failed",
      form: kind,
      email,
      page,
      received: new Date().toISOString(),
      fields,
      notice,
    });
  }

  // Background work: a CRM outage or a bounced receipt must never reach the visitor.
  const background = (async () => {
    const crm = await crmPush(env, {
      source: "website",
      form: kind,
      email,
      page,
      fields,
      received: new Date().toISOString(),
    });
    if (crm.status === "err") {
      console.error(JSON.stringify({ evt: "crm", form: kind, ok: false, msg: crm.error }));
    }

    const replyTo = env.LEAD_REPLY_TO || String(env.LEAD_TO || "").split(",")[0].trim() || undefined;
    const receipt = await sendMail(env, {
      to: email,
      subject: "We received your enquiry — G&W Biotechnologie GmbH",
      text: receiptText(fields, env),
      replyTo,
    });
    if (receipt.status === "failed") {
      console.error(JSON.stringify({ evt: "receipt_failed", form: kind, attempts: receipt.attempts, msg: receipt.error }));
    }

    logLine("lead", {
      form: kind,
      ok: true,
      mail: mail.status,
      crm: crm.status,
      receipt: receipt.status,
      rl: rl.off ? "off" : "ok",
      ms: Date.now() - started,
      fields: fieldShape(fields),
    });
  })().catch((e) => {
    console.error(JSON.stringify({ evt: "lead_bg_err", form: kind, msg: String((e && e.message) || e) }));
  });

  if (ctx && typeof ctx.waitUntil === "function") ctx.waitUntil(background);
  else await background;

  return json({ ok: true, mail: mail.status === "skipped" ? "queued" : mail.status });
}

async function handleCoa(req, env) {
  const { data, error } = await readJson(req);
  if (error) return bad(error);

  const lot = String((data.fields && (data.fields.lot_number || data.fields["lot number"])) || "")
    .trim()
    .toUpperCase()
    .replace(/[^A-Z0-9-]/g, "")
    .slice(0, 24);
  if (!lot) return bad("lot number required");

  if (!env.COA_INDEX) return json({ ok: true, found: false, reason: "index not configured" });

  const hit = await env.COA_INDEX.get(lot, "json");
  if (!hit) {
    console.log(JSON.stringify({ evt: "coa_miss", lot }));
    return json({ ok: true, found: false });
  }
  console.log(JSON.stringify({ evt: "coa_hit", lot, file: hit.file }));
  return json({
    ok: true,
    found: true,
    url: `${env.COA_BASE || "/docs/"}${hit.file}`,
    sku: hit.sku || "",
    released: hit.released || "",
  });
}

async function handleChat(req, env) {
  if (!env.CHAT_API_URL) {
    return json({ ok: false, error: "assistant not configured" }, 501);
  }
  const { data, error } = await readJson(req);
  if (error) return bad(error);

  const messages = Array.isArray(data.messages) ? data.messages.slice(-8) : [];
  if (!messages.length) return bad("messages required");

  const r = await fetch(env.CHAT_API_URL, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      ...(env.CHAT_API_KEY ? { authorization: `Bearer ${env.CHAT_API_KEY}` } : {}),
    },
    body: JSON.stringify({ messages, temperature: 0.2, max_tokens: 600 }),
  });
  if (!r.ok) return json({ ok: false, error: `upstream ${r.status}` }, 502);

  const out = await r.json();
  const reply = out.choices?.[0]?.message?.content || "";
  console.log(JSON.stringify({ evt: "chat", len: reply.length }));
  return json({ ok: true, reply, sources: [] });
}

/* ------------------------------------------------------------------ entry */

export default {
  async fetch(req, env, ctx) {
    const url = new URL(req.url);
    const route = url.pathname.replace(/\/+$/, "");

    if (req.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          "access-control-allow-origin": url.origin,
          "access-control-allow-methods": "POST, GET, OPTIONS",
          "access-control-allow-headers": "content-type",
          "access-control-max-age": "86400",
        },
      });
    }

    try {
      if (route === "/api/health") {
        return json({
          ok: true,
          ts: Date.now(),
          cfg: {
            turnstile: Boolean(env.TURNSTILE_SECRET),
            rateLimit: Boolean(env.LEAD_KV),
            crm: Boolean(env.CRM_WEBHOOK),
            mail: Boolean(env.RESEND_API_KEY && env.LEAD_TO),
          },
        });
      }
      if (route === "/api/lead" && req.method === "POST") return await handleLead(req, env, ctx);
      if (route === "/api/coa" && req.method === "POST") return await handleCoa(req, env);
      if (route === "/api/chat" && req.method === "POST") return await handleChat(req, env);
      return bad("not found", 404);
    } catch (e) {
      console.error(JSON.stringify({ evt: "error", route, msg: String(e && e.message) }));
      return bad("internal error", 500);
    }
  },
};
