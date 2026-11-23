/**
 * GitHub OAuth bridge for Decap CMS (/admin on the G&W site).
 *
 * Routes
 *   GET /auth      -> 302 to github.com/login/oauth/authorize
 *   GET /callback  -> exchanges code for a token, hands it to the CMS popup
 *   GET /health    -> config check, no secrets exposed
 *
 * Env (wrangler secret put)
 *   GITHUB_CLIENT_ID
 *   GITHUB_CLIENT_SECRET
 *   STATE_SECRET   optional; defaults to GITHUB_CLIENT_SECRET
 *
 * The token is never logged and never stored: it goes straight into a
 * postMessage payload for the window that opened the popup.
 */

const SCOPE = "repo";
const STATE_TTL_MS = 10 * 60 * 1000;
const enc = new TextEncoder();

const html = (body, status = 200) =>
  new Response(body, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-store",
      "x-frame-options": "DENY",
      "referrer-policy": "no-referrer",
    },
  });

function b64url(bytes) {
  let s = "";
  for (const b of new Uint8Array(bytes)) s += String.fromCharCode(b);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function signState(ts, secret) {
  const key = await crypto.subtle.importKey(
    "raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  const mac = await crypto.subtle.sign("HMAC", key, enc.encode(ts));
  return `${ts}.${b64url(mac).slice(0, 16)}`;
}

async function checkState(state, secret) {
  if (!state || state.indexOf(".") === -1) return false;
  const ts = state.split(".")[0];
  if (!/^\d+$/.test(ts)) return false;
  if (Date.now() - Number(ts) > STATE_TTL_MS) return false;
  return state === (await signState(ts, secret));
}

/** Hand the token to Decap: it listens for this exact message shape. */
function handoffPage(token) {
  const payload = JSON.stringify({ token, provider: "github" });
  return `<!doctype html><meta charset="utf-8"><title>Signed in</title>
<body style="font:15px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;padding:32px;color:#2a3142">
<p id="msg">Finishing sign-in…</p>
<script>
(function () {
  var payload = ${JSON.stringify(payload)};
  var sent = false;
  function send() {
    if (sent || !window.opener) return;
    sent = true;
    window.opener.postMessage("authorization:github:success:" + payload, "*");
    document.getElementById("msg").textContent = "Signed in — you can close this window.";
  }
  window.addEventListener("message", function (e) {
    if (typeof e.data === "string" && e.data.indexOf("authorizing:github") === 0) send();
  }, false);
  if (window.opener) { window.opener.postMessage("authorizing:github", "*"); }
  setTimeout(send, 700);
})();
</script>`;
}

export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const route = url.pathname.replace(/\/+$/, "");

    if (route === "/health") {
      return new Response(JSON.stringify({
        ok: true,
        configured: Boolean(env.GITHUB_CLIENT_ID && env.GITHUB_CLIENT_SECRET),
        hasStateSecret: Boolean(env.STATE_SECRET || env.GITHUB_CLIENT_SECRET),
      }), { headers: { "content-type": "application/json", "cache-control": "no-store" } });
    }

    if (!env.GITHUB_CLIENT_ID || !env.GITHUB_CLIENT_SECRET) {
      return html("<p>OAuth is not configured on this worker.</p>", 503);
    }
    const secret = env.STATE_SECRET || env.GITHUB_CLIENT_SECRET;

    // Mounted under a path prefix on the Node bridge (/oauth); empty on Cloudflare.
    const prefix = env.OAUTH_PREFIX || "";

    if (route === "/auth") {
      const state = await signState(String(Date.now()), secret);
      const target = new URL("https://github.com/login/oauth/authorize");
      target.searchParams.set("client_id", env.GITHUB_CLIENT_ID);
      target.searchParams.set("scope", SCOPE);
      target.searchParams.set("redirect_uri", `${url.origin}${prefix}/callback`);
      target.searchParams.set("state", state);
      return Response.redirect(target.toString(), 302);
    }

    if (route === "/callback") {
      if (url.searchParams.get("error")) {
        return html("<p>GitHub returned an error. Close this window and try again.</p>", 400);
      }
      if (!(await checkState(url.searchParams.get("state"), secret))) {
        return html("<p>Sign-in expired or was tampered with. Close this window and try again.</p>", 400);
      }
      const code = url.searchParams.get("code");
      if (!code) return html("<p>Missing authorization code.</p>", 400);

      let data = {};
      try {
        const r = await fetch("https://github.com/login/oauth/access_token", {
          method: "POST",
          headers: { "content-type": "application/json", accept: "application/json" },
          body: JSON.stringify({
            client_id: env.GITHUB_CLIENT_ID,
            client_secret: env.GITHUB_CLIENT_SECRET,
            code,
            redirect_uri: `${url.origin}${prefix}/callback`,
          }),
        });
        data = await r.json();
      } catch (e) {
        console.error(JSON.stringify({ evt: "oauth_exchange_err", msg: String(e && e.message) }));
        return html("<p>Could not reach GitHub. Try again in a minute.</p>", 502);
      }

      if (!data.access_token) {
        console.error(JSON.stringify({ evt: "oauth_no_token", err: String(data.error || "") }));
        return html("<p>GitHub did not return a token. Check the OAuth app's client secret.</p>", 400);
      }
      console.log(JSON.stringify({ evt: "oauth_ok", user: Boolean(data.access_token) }));
      return html(handoffPage(String(data.access_token)));
    }

    return html("<p>Not found.</p>", 404);
  },
};
