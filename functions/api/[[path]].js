/**
 * Pages Function: mounts the site API under the same origin as the static site.
 *
 * Same origin means the forms need no CORS, no custom domain and no separate
 * workers.dev host — the exact same request/response contract as server/worker.js.
 *
 * Bindings live on the Pages project (Settings -> Functions):
 *   LEAD_KV            KV namespace for rate limiting and the failed-mail archive
 *   ENVIRONMENT        "production" enables the fail-closed Turnstile check
 *   LEAD_FROM, LEAD_TO, TURNSTILE_SECRET, RESEND_API_KEY, CRM_WEBHOOK …
 */
import worker from "../../server/worker.js";

export const onRequest = (context) =>
  worker.fetch(context.request, context.env, { waitUntil: context.waitUntil });
