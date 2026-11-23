# node-bridge — 把 worker.js 跑到自己的服务器上

用于**无法访问 `*.workers.dev`** 的机房（例如国内云主机：DNS 被污染到 Facebook 的 IP，
SNI 也会被重置）。逻辑一行不改，`server/worker.js` 原样复用。

## 为什么需要这层

`worker.js` 是 Cloudflare Worker 形态（`export default { fetch }`），直接用 Node 跑不了，
还缺两样运行时设施：

| Cloudflare 有 | Node 没有 | 桥接层怎么补 |
|---|---|---|
| 全局 `crypto.subtle` | Node 18 无全局 crypto | `webcrypto` 挂到 `globalThis` |
| `env.LEAD_KV` / `env.COA_INDEX` | 无 KV | 进程内 `Map` + `expirationTtl` |
| `ctx.waitUntil` | 无 | 立即执行的 promise（不阻塞响应） |
| `request.cf` / `cf-connecting-ip` | 无 | 由 nginx 的 `X-Real-IP` 补上 |

## 部署

```bash
# 1. 目录
mkdir -p /opt/tl-api/node-bridge

# 2. 文件（从仓库根目录执行）
scp server/worker.js                    root@<host>:/opt/tl-api/worker.js
scp server/node-bridge/bridge.js        root@<host>:/opt/tl-api/node-bridge/
scp server/node-bridge/package.json     root@<host>:/opt/tl-api/
scp server/node-bridge/tl-api.service   root@<host>:/etc/systemd/system/

# 3. 启动
systemctl daemon-reload
systemctl enable --now tl-api
systemctl status tl-api --no-pager

# 4. nginx 反代（配置见同目录 nginx.conf）
cp nginx.conf /etc/nginx/sites-available/tl.conf
nginx -t && systemctl reload nginx
```

## 环境变量

改 `tl-api.service` 的 `Environment=` 行，或在 `/etc/systemd/system/tl-api.service.d/override.conf`
里覆盖，然后 `systemctl daemon-reload && systemctl restart tl-api`。

| 变量 | 说明 |
|---|---|
| `ENVIRONMENT` | `staging` 时缺 Turnstile 密钥也放行；`production` 会 fail-closed 返回 503 |
| `LEAD_TO` | 收件人，逗号分隔。**不填则不发信** |
| `LEAD_FROM` | 发件人，必须是 Resend 已验证的域名 |
| `RESEND_API_KEY` | 不填则邮件跳过（表单仍返回 200） |
| `TURNSTILE_SECRET` | 与前端 `turnstile_sitekey` 必须成对 |
| `CRM_WEBHOOK` | 可选，2 秒超时，失败不影响表单 |
| `RECEIPT_SIGNER` | 回执署名，需真实姓名 |
| `IP_SALT` | 限流键的盐 |
| `PORT` | 默认 8081，只监听 127.0.0.1 |

## 验证

```bash
curl -s http://127.0.0.1:8081/api/health                 # rateLimit 应为 true
curl -s -X POST http://127.0.0.1/api/lead \
  -H 'content-type: application/json' \
  -d '{"form":"contact","fields":{"full_name":"T","work_email":"t@example.com"}}'
# 连发 6 次，第 6 次应返回 429
```

## 已知限制

- **限流计数在内存里**，`restart` 会清零；多实例部署时各算各的。要跨重启就换 Redis/SQLite。
- **失败邮件归档**（`failed:*`）同样只在内存，进程退出即丢。生产建议改持久化。
- 单进程、无集群。8.4 MB 静态站 + 低频表单，单进程足够；要扛并发就上 `pm2 -i` 或 Node 集群。

## 邮件：SMTP 旁路（smtp_send.py）

`worker.js` 调的是 `https://api.resend.com/emails`。没有 Resend 账号或无法验证域名时，
`bridge.js` 会在运行时拦截这个 URL，转给 `smtp_send.py`，由它用标准库 `smtplib`
走已认证的邮箱发出去。**`worker.js` 一行不改。**

```
bridge.js: globalThis.fetch 被包装 → 命中 api.resend.com → POST 127.0.0.1:8082/send
smtp_send.py: smtplib.SMTP_SSL(smtp.exmail.qq.com:465) → login → send_message
```

需要的配置（`/etc/tl-mail.env`，权限 600）：

```
SMTP_HOST=smtp.exmail.qq.com
SMTP_PORT=465
SMTP_USER=someone@yourdomain.com
SMTP_PASS=<客户端专用密码，不是登录密码>
PORT=8082
```

`/etc/tl-api.env` 里必须给 `RESEND_API_KEY` 一个**非空假值**（如 `smtp-sidecar`），
否则 `sendMail()` 会直接返回 `skipped`，根本不会发出请求。

注意：

- 腾讯企业邮要求 `From` 的地址与登录账号一致，否则拒发。显示名可以随便写，
  例如 `T&L Biotechnology <mailbox@domain.cn>`。
- 这套只在 Node 上有效。Cloudflare Worker 不支持原始 TCP，那边必须用 Resend 之类的 HTTP API。
- 发送记录在 `journalctl -u tl-mail`，事件名 `smtp_sent` / `smtp_error`。

## 与 Cloudflare 的关系

两者跑的是**同一份 `worker.js`**：

| 环境 | 跑在哪 | 何时用 |
|---|---|---|
| 海外/能访问 workers.dev | Cloudflare Worker | 首选，免费、全球边缘 |
| 国内云主机 | 本目录的 Node 桥接 | 备选，绕开网络阻断 |

切换时只改 nginx 的 `proxy_pass` 目标，前端和 worker 代码都不动。
