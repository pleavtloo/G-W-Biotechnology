# server/ — 站点 API

三个端点，各自独立失败，互不阻塞。静态页面由 CDN 托管，这里只处理 `/api/*`。

| 端点 | 用途 | 失败时 |
|---|---|---|
| `POST /api/lead` | 询价、经销商申请、CTA 订阅 | 前端显示兜底邮箱，不白屏 |
| `POST /api/coa` | 按批次号查 COA | 返回 `found:false`，转 QA 人工 |
| `POST /api/chat` | AI 客服 P1（检索问答） | 501，前端降级为转人工 |
| `GET /api/health` | 探活 | — |

## 本地跑通（不需要 Cloudflare 账号）

```bash
python tools/build_dist.py        # 生成 dist/
python server/dev_server.py 8080  # 静态站 + 真实 API
# 打开 http://127.0.0.1:8080/contact.html 提交表单
# 提交记录写入 server/outbox/YYYY-MM-DD.jsonl
```

演示规则：COA 查询中，批次号含数字即命中，返回一份样例 PDF。

## 生产部署（Cloudflare）

```bash
npm i -g wrangler
cd server
wrangler secret put RESEND_API_KEY     # 事务邮件
wrangler secret put LEAD_TO            # 收件人，逗号分隔
wrangler secret put TURNSTILE_SECRET   # 可选，开了就必须带 token
wrangler deploy
```

然后在 Pages 项目里把 `/api/*` 路由到这个 worker。

**发信域必须先配 SPF / DKIM / DMARC**，否则询价邮件会进垃圾箱——这是最常见的上线事故。

## 环境变量

| 变量 | 必需 | 说明 |
|---|---|---|
| `RESEND_API_KEY` | 是 | 事务邮件服务 |
| `LEAD_TO` | 是 | 收件人列表 |
| `LEAD_FROM` | 否 | 已验证发信地址 |
| `TURNSTILE_SECRET` | 否 | 开启后前端需带 token |
| `COA_INDEX` | 否 | KV 命名空间：批次号 → `{file, sku, released}` |
| `COA_BASE` | 否 | COA 文件公共前缀 |
| `CHAT_API_URL` | 否 | OpenAI 兼容的 chat completions 端点 |
| `CHAT_API_KEY` | 否 | 上游鉴权 |

## 安全设计

- 请求体上限 16 KB，字段上限 12 个，超限直接丢弃
- 不把用户输入回显到响应（无反射型 XSS 面）
- 蜜罐字段 `website_url`：填了即静默丢弃，不报错（避免教对手绕过）
- 邮箱格式在服务端二次校验，不信任前端
- 日志只记事件与字段名，不记完整正文（避免 PII 落日志）
- 错误一律返回 JSON，不返回堆栈

## 未做（上线前需补）

- [ ] 频率限制（现在只有蜜罐；建议按 IP + 端点做 KV 计数）
- [ ] CRM 写入（HubSpot / Pipedrive / 销售易）
- [ ] 自动回执邮件（现在只有内部通知）
- [ ] 对话日志留存 6 个月（合规要求）
- [ ] `COA_INDEX` 的真实数据接入
