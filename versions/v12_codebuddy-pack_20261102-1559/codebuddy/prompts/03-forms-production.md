# P03 · 表单接生产：Turnstile、发信、CRM、限流

**目标**：把 `/api/lead` 从"能收"变成"收得住、追得到、不丢"。

**前置**：P00。当前 `server/worker.js` 已有骨架，这一步补生产必需的四件事。

**先读**：`CODEBUDDY.md`、`server/worker.js`、`server/README.md`、
`website/assets/js/main.js` 里的表单段

---

## 现状

已实现：JSON 校验、字段清洗、蜜罐、可选 Turnstile、Resend 发信、不回显输入。
未实现：**限流、CRM 写入、自动回执、失败重试**。

## 任务

### 1. Turnstile 默认开启

- `check.py` 或构建时检查：生产配置里 `TURNSTILE_SECRET` 为空要在 `wrangler.toml` 注释里标红
- 前端：在表单里注入 Turnstile 脚本，`data-sitekey` 从 `window.TL.turnstileSiteKey` 读（构建注入）
- 无 sitekey 时（本地开发）跳过，**不能因此让本地表单不可用**

### 2. 限流（关键）

现在只有蜜罐，挡不住定向刷。

- 用 KV 做滑动窗口：key = `rl:<ip>:<endpoint>`，5 分钟内最多 5 次
- 超限返回 `429` + `Retry-After`，前端显示"提交过于频繁，请 5 分钟后再试，或直接邮件"
- **不要静默丢弃**——正常用户被误伤时必须有提示

### 3. CRM 写入

- 新增 `env.CRM_WEBHOOK`：POST 一条扁平 JSON（字段见下），超时 2 秒
- 失败**不能**让表单报错（`ctx.waitUntil` 里做，失败只记日志）
- 载荷：
  ```json
  { "source": "website", "form": "contact", "email": "...", "page": "/contact.html",
    "fields": { "...": "..." }, "received": "2026-11-02T15:00:00Z" }
  ```

### 4. 自动回执

- 给提交人发一封确认信（同一发信域，`reply-to` 指向销售组）
- 内容：我们收到了什么（回显他填的关键字段）+ 一个真实的人名 + 一个工作日内回复的承诺
- **不要在回执里承诺价格或交期**

### 5. 失败重试与观测

- 发信失败重试 2 次（指数退避 300ms / 900ms），仍失败则写 `console.error` 并把提交存进 KV
  `failed:<ts>`（保留 7 天，供人工补发）
- 每个事件结构化打日志：`{evt, form, ok, mail, crm, ms}`

## 约束

- 不引入第三方 SDK，全部用 `fetch`
- 不在日志里写用户正文（只写字段名与长度）
- 限流键用 IP 的**哈希**，不存明文
- 前端改动只动 `main.js` 的表单段与 `build_site.py` 注入的 sitekey，不动样式结构

## 验收

```bash
python server/dev_server.py 8080
# 1) 正常提交 -> 200，outbox 有记录
# 2) 连点 6 次 -> 第 6 次 429
# 3) 填蜜罐字段 -> 200 但 outbox 无记录
# 4) 邮箱留空 -> 400
```

在 `dev_server.py` 里把限流与 CRM 也实现一份（用内存字典即可），保证本地能测。

## 交付

- `server/worker.js`：限流、CRM、回执、重试
- `server/dev_server.py`：同逻辑的本地实现
- `main.js`：Turnstile 注入 + 429 文案
- `server/README.md`：新增环境变量说明
- 四条验收的实际输出

## 备注

发信域 SPF/DKIM/DMARC 是客户侧的事，但**上线前必须确认**——不配好，询价全进垃圾箱。
在回复里单独提醒一次。
