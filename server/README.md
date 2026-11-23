# server/ — 站点 API

三个端点，各自独立失败，互不阻塞。静态页面由 CDN 托管，这里只处理 `/api/*`。

| 端点 | 用途 | 失败时 |
|---|---|---|
| `POST /api/lead` | 询价、经销商申请、CTA 订阅 | 前端显示兜底邮箱，不白屏 |
| `POST /api/coa` | 按批次号查 COA | 返回 `found:false`，转 QA 人工 |
| `POST /api/chat` | AI 客服 P1（检索问答） | 501，前端降级为转人工 |
| `GET /api/health` | 探活 + 配置自检（`cfg.turnstile/rateLimit/crm/mail`） | — |

## 本地跑通（不需要 Cloudflare 账号）

```bash
python tools/build_dist.py        # 生成 dist/
python server/dev_server.py 8080  # 静态站 + 真实 API
# 打开 http://127.0.0.1:8080/contact.html 提交表单
# 提交记录写入 server/outbox/YYYY-MM-DD.jsonl
```

演示规则：COA 查询中，批次号含数字即命中，返回一份样例 PDF。

本地不设 `TURNSTILE_SECRET`，人机校验自动跳过；限流、CRM、回执都按生产同一套逻辑跑，
所以下面四条验收在本地就是真实行为。

### 四条验收

```bash
python server/dev_server.py 8080

# 1) 正常提交 -> 200，outbox 有记录
curl -s -X POST http://127.0.0.1:8080/api/lead -H "content-type: application/json" \
  -d '{"form":"contact","fields":{"full_name":"Jane Doe","work_email":"jane@company.com","organisation":"Acme"}}'

# 2) 连点 6 次 -> 第 6 次 429（先清窗口，否则上一轮计数还在）
curl -s -X POST http://127.0.0.1:8080/api/_reset
for i in 1 2 3 4 5 6; do curl -s -o /dev/null -w "%{http_code} " -X POST \
  http://127.0.0.1:8080/api/lead -H "content-type: application/json" \
  -d '{"form":"contact","fields":{"work_email":"jane@company.com"}}'; done

# 3) 填蜜罐字段 -> 200 但 outbox 无记录
curl -s -X POST http://127.0.0.1:8080/api/lead -H "content-type: application/json" \
  -d '{"form":"contact","fields":{"work_email":"jane@company.com","website_url":"spam"}}'

# 4) 邮箱留空 -> 400
curl -s -X POST http://127.0.0.1:8080/api/lead -H "content-type: application/json" \
  -d '{"form":"contact","fields":{"full_name":"Jane Doe"}}'
```

`POST /api/_reset` 只存在于 `dev_server.py`：清空内存限流窗口，让第 2 条可反复复现。
生产没有这个路由。

## 生产部署（Cloudflare）

```bash
npm i -g wrangler
cd server
wrangler kv namespace create LEAD_KV    # 限流 + 失败补发归档，id 填回 wrangler.toml
wrangler secret put RESEND_API_KEY      # 事务邮件
wrangler secret put LEAD_TO             # 收件人，逗号分隔
wrangler secret put TURNSTILE_SECRET    # 生产必填，缺了 /api/lead 直接 503
wrangler deploy
```

然后在 Pages 项目里把 `/api/*` 路由到这个 worker。
公开 sitekey 填 `tools/content.py` 的 `COMPANY["turnstile_sitekey"]`，然后重建站点——
两者必须来自同一个 Turnstile widget，否则校验永远不通过。

**发信域必须先配 SPF / DKIM / DMARC**，否则询价邮件会进垃圾箱——这是最常见的上线事故。

## 环境变量

| 变量 | 必需 | 说明 |
|---|---|---|
| `ENVIRONMENT` | 是 | `wrangler.toml` 固定为 `production`；缺 `TURNSTILE_SECRET` 时接口 503 |
| `RESEND_API_KEY` | 是 | 事务邮件服务 |
| `LEAD_TO` | 是 | 收件人列表 |
| `TURNSTILE_SECRET` | 是 | 生产必填；本地留空即跳过校验 |
| `LEAD_KV` | 是 | KV 命名空间：限流计数 `rl:*` + 失败归档 `failed:*` |
| `LEAD_FROM` | 否 | 已验证发信地址 |
| `LEAD_REPLY_TO` | 否 | 回执的 reply-to，默认取 `LEAD_TO` 第一个 |
| `RECEIPT_SIGNER` | 否 | 回执署名（真实姓名 + 职位），缺省为团队署名 |
| `CRM_WEBHOOK` | 否 | CRM 入站地址；不支持时跳过，不影响表单 |
| `IP_SALT` | 否 | 限流键哈希的盐 |
| `COA_INDEX` | 否 | KV 命名空间：批次号 → `{file, sku, released}` |
| `COA_BASE` | 否 | COA 文件公共前缀 |
| `CHAT_API_URL` | 否 | OpenAI 兼容的 chat completions 端点 |
| `CHAT_API_KEY` | 否 | 上游鉴权 |

## 限流

- 键：`rl:<ip_hash>:lead`，`ip_hash` = `SHA-256(ip|IP_SALT)` 前 16 位，**不落明文 IP**
- 窗口：5 分钟滑动，每窗口最多 5 次；超限 `429` + `Retry-After` 头 + `retryAfter` 字段
- 存储：`LEAD_KV`，值是该窗口内的时间戳数组，`expirationTtl` 300 秒
- 未绑 `LEAD_KV` 时限流关闭并在日志里写 `rl:"off"`，**不阻断提交**（灰度期可用）
- KV 最终一致 + 单键写频率限制，并发突刺可能漏计 1-2 次；表单场景可接受，不引入 Durable Objects

前端拿到 429 会显示"提交过于频繁，请 N 分钟后再试，或直接邮件"，链接是 `mailto:`。

## CRM 写入

`env.CRM_WEBHOOK` 存在时 POST 一条扁平记录，2 秒超时，在 `ctx.waitUntil` 里执行：

```json
{ "source": "website", "form": "contact", "email": "jane@company.com",
  "page": "/contact.html", "fields": { "...": "..." }, "received": "2026-11-02T15:00:00Z" }
```

CRM 挂了只打 `console.error`，访客照常看到成功提示。

## 自动回执

- 收件人 = 提交邮箱，`reply-to` = `LEAD_REPLY_TO`（默认销售组）
- 只回显白名单字段（姓名 / 机构 / 意向 / 应用 / 留言），各截 200 字，不回显邮箱
- 署名取 `RECEIPT_SIGNER`，未配置时用团队署名——**不编造人名**
- 正文明确"这只是收件确认，报价与交期由对接人在回信里给出"，不含任何价格/交期数字

## 重试与观测

- 内部通知信：1 次首发 + 2 次重试（300ms / 900ms），每次 5 秒超时
- 三次都失败：`console.error` + 写 `LEAD_KV` 的 `failed:<ISO8601>`（含完整正文与字段，TTL 7 天，供人工补发）
- 每个提交一行结构化日志，字段固定：
  `{evt:"lead", form, ok, mail, crm, receipt, rl, ms, fields:[{k,len}]}`
- 日志只有事件名、字段名、长度；**不写用户正文、不写明文 IP**

## 安全设计

- 请求体上限 16 KB，字段上限 12 个，超限直接丢弃
- 不把用户输入回显到响应（无反射型 XSS 面）
- 蜜罐字段 `website_url`：填了即静默丢弃，不报错（避免教对手绕过），且不消耗限流配额
- 邮箱格式在服务端二次校验，不信任前端
- 限流键只用 IP 哈希；内部通知邮件保留 `IP:` 行供人工排查滥用
- 错误一律返回 JSON，不返回堆栈

## 上线前仍需补

- [ ] `RECEIPT_SIGNER`：客户提供一个真实姓名 + 职位（现为团队署名）
- [ ] Turnstile sitekey（`tools/content.py`）+ secret（`wrangler secret put`）配对
- [ ] `LEAD_KV` 真实 namespace id
- [ ] `CRM_WEBHOOK` 真实地址（HubSpot / Pipedrive / 销售易）
- [ ] SPF / DKIM / DMARC 在发信域上验证
- [ ] 对话日志留存 6 个月（合规要求）
- [ ] `COA_INDEX` 的真实数据接入
