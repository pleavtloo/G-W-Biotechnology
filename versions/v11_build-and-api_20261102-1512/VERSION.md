# v11 — 生产构建 + SEO + 表单 API

## 决策（已锁定）
仅英文 / 公开价格 / AI 仅 P1 / 境外部署（Cloudflare Pages）

## 新增
### 构建
- `tools/build_dist.py`：输出 `dist/`，HTML/CSS 压缩、排除设计评审页
- 生成 `sitemap.xml`（52 URL，含 42 个 SKU）、`robots.txt`、`_headers`、`_redirects`
- 三级输出：`website/`（开发）→ `dist/`（部署）→ `versions/`（快照）

### SEO
- `head()` 统一生成 canonical / OG / Twitter Card
- 结构化数据：Organization、BreadcrumbList（全站）、FAQPage（resources）、
  ContactPage（contact）、Product + Offer（产品页，前端注入）
- 新增 404 页（noindex，四向导航）

### 表单与 API
- 前端：真实 POST、三态（提交中/成功/失败）、蜜罐 `website_url` 静默丢弃、
  失败态给 mailto 兜底、`aria-busy`
- `server/worker.js`：`/api/lead` `/api/coa` `/api/chat`(501) `/api/health`，
  16KB/12 字段上限、Turnstile 可选、Resend 发信、不回显输入
- `server/dev_server.py`：本地静态站 + 真实 API，提交写 `server/outbox/`
- `server/wrangler.toml`、`server/README.md`

## 实测
- 联系表单端到端提交成功，字段键 `full_name / work_email / organisation / ...`
- COA 查询命中返回文件；无效邮箱被 400 拒绝；蜜罐静默 200
- dist 12 页 0 缺失引用，无 design-* 泄漏

## 回滚
覆盖回 `website/`、`tools/`、`server/`、两个 md；`dist/` 可整目录删除后重跑。
