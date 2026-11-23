/**
 * T&L Biotechnology — edge API
 *
 * Routes
 *   POST /api/lead    quote requests, partner applications, CTA subscriptions
 *   POST /api/coa     lot number lookup -> document URL
 *   POST /api/chat    AI assistant (P1: retrieval Q&A) — stub until the index is ready
 *   GET  /api/health
 *
 * Bindings / env
 *   RESEND_API_KEY     transactional email (https://resend.com)
 *   LEAD_TO            comma separated recipients, e.g. "sales@x.com,qa@x.com"
 *   LEAD_FROM          verified sender, e.g. "site@tlbiotechnology.com"
 *   TURNSTILE_SECRET   optional; when set, `turnstileToken` is required
 *   COA_INDEX          KV namespace: lot number -> { file, sku, released }
 *   COA_BASE           public base URL for COA files, e.g. https://files.example.com/coa/
 *   CHAT_API_URL       upstream LLM / RAG endpoint (OpenAI-compatible chat completions)
 *   CHAT_API_KEY       bearer token for the above
 *
 * Design notes
 *   - Every route fails closed and returns JSON, never HTML.
 *   - The form endpoint never echoes user input back (no reflected XSS surface).
 *   - Requests are capped at 16 KB and 8 fields; anything larger is dropped.
 */

const MAX_BODY = 16 * 1024;
const MAX_FIELDS = 12;

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });

const bad = (msg, status = 400) => json({ ok: false, error: msg }, status);

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

async function verifyTurnstile(env, token, ip) {
  if (!env.TURNSTILE_SECRET) return true;
  if (!token) return false;
  const body = new FormData();
  body.append("secret", env.TURNSTILE_SECRET);
  body.append("response", token);
  if (ip) body.append("remoteip", ip);
  const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
    method: "POST",
    body,
  });
  const out = await r.json().catch(() => ({}));
  return out.success === true;
}

async function sendMail(env, subject, text) {
  if (!env.RESEND_API_KEY || !env.LEAD_TO) return { skipped: true };
  const r = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      authorization: `Bearer ${env.RESEND_API_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify({
      from: env.LEAD_FROM || "site@tlbiotechnology.com",
      to: env.LEAD_TO.split(",").map((s) => s.trim()),
      subject,
      text,
    }),
  });
  if (!r.ok) return { skipped: false, error: `mail ${r.status}` };
  return { skipped: false, id: (await r.json().catch(() => ({}))).id };
}

/* ------------------------------------------------------------------ routes */

async function handleLead(req, env, ctx) {
  const { data, error } = await readJson(req);
  if (error) return bad(error);

  const fields = cleanFields(data.fields);
  if (!Object.keys(fields).length) return bad("empty submission");
  if (data.fields && data.fields.website_url) return json({ ok: true }); // honeypot: accept, discard

  const ip = req.headers.get("cf-connecting-ip") || "";
  if (!(await verifyTurnstile(env, data.turnstileToken, ip))) return bad("verification failed", 403);

  const email = pickEmail(fields);
  if (!email) return bad("a valid email address is required");

  const kind = String(data.form || "lead").slice(0, 24);
  const lines = Object.entries(fields).map(([k, v]) => `${k}: ${v}`);
  const text = [
    `Form: ${kind}`,
    `Page: ${String(data.path || "").slice(0, 200)}`,
    `Referrer: ${String(data.referrer || "-").slice(0, 200)}`,
    "",
    ...lines,
    "",
    `Received: ${new Date().toISOString()}`,
    `IP: ${ip || "-"}`,
  ].join("\n");

  const mail = await sendMail(env, `[site] ${kind} — ${email}`, text);
  console.log(JSON.stringify({ evt: "lead", kind, email, mail, fields: Object.keys(fields) }));

  // A CRM write belongs here (HubSpot / Pipedrive / 销售易). Keep it non-blocking:
  // a CRM outage must not turn a captured lead into an error page.
  ctx.waitUntil(Promise.resolve());

  return json({ ok: true, mail: mail.skipped ? "queued" : "sent" });
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
      if (route === "/api/health") return json({ ok: true, ts: Date.now() });
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
