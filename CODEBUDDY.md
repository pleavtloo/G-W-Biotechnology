# CODEBUDDY.md — T&L Biotechnology 官网

> 这份文件放在仓库根目录，CodeBuddy 每次会话自动读取。它是**约束**，不是介绍。
> 冲突时以本文件为准，其次 `DESIGN-LANGUAGE.md`，再次口头描述。

## 1. 项目是什么

T&L Biotechnology 的英文官网。定位：AI for science，生命科学工具（磁珠 / 抗体 / 重组蛋白 / 培养基），
附带表达设计服务与产能网络。

- 受众：研发科学家、采购、QA/RA、经销商、投资人（四类，判断标准不同）
- 目标：让访客在 30 秒内理解「我们是谁、卖什么、凭什么信」，并把询价送进来
- 站点语言：**仅英文**（不做中文版，不做 hreflang）

## 2. 技术栈（不要更换）

| 层 | 选型 | 约束 |
|---|---|---|
| 页面 | 静态 HTML，Python 脚本生成 | 不引入 React/Vue/Next/Astro |
| 样式 | 单文件原生 CSS，自定义属性驱动 | 不引入 Tailwind/Bootstrap/预处理器 |
| 脚本 | 原生 JS，ES5 语法，IIFE 封装 | 不引入 jQuery/框架/打包器（esbuild 仅用于压缩，可选） |
| 数据 | `tools/content.py` → 构建时生成 `data.js` | 页面不直接读 API 拿产品数据 |
| 文档 | fpdf2 生成 PDF | 不改版式不加依赖 |
| API | Cloudflare Worker（`server/worker.js`） | 无 Node 常驻服务 |
| 构建 | Python 3.13 | 不引入 npm 构建链 |

新增任何依赖前必须先问，并说明为什么现有栈做不到。

### 2.1 例外条款：后台内容管理（2026-11-03 批准）

在此以前，内容只能由工程师改 Python 再重新构建。市场部需要自助维护产品资料，因此批准以下增量。
它们**只服务于内容编辑**，不改变站点渲染方式：站点仍然是纯静态，仍然由 Python 脚本在构建期生成。

允许新增：

| 组件 | 作用 | 约束 |
|---|---|---|
| `content/*.yaml` | 唯一内容源（产品 / 应用 / FAQ / 文章 / 站点设置 / 分类） | 字段契约见 `CONTENT-SCHEMA.md`；`tools/content.py` 降为加载器 |
| `website/admin/` | 后台编辑界面（Decap CMS） | 纯静态页面 + 一次外链脚本；`noindex`；不进 sitemap |
| `.github/workflows/` | CI：`build_site → build_docs → build_dist → check.py` → 发布 | 门禁不过禁止发布，禁止 `|| true` |
| `server/oauth-worker/` | GitHub OAuth 回调（独立 Worker，独立部署） | 只做鉴权，不存内容、不碰站点数据 |

仍然禁止：

- React / Vue / Next / Astro、Tailwind、任何前端框架或打包器进入**主站**
- 页面在运行时从数据库或 API 读产品内容（站点必须保持纯静态，内容在构建期注入）
- 绕过 `check.py`（包括在 CI 里忽略失败、手改 `dist/`）
- 后台可编辑 `slug`、`site_url`、`turnstile_sitekey`（改了会断外链或破坏部署）
- 用 npm 脚本替代 `tools/*.py` 作为构建入口

优先级：本条款只放宽「不能有后台」，不放宽第 5 节的任何内容规则。后台改出来的文案，
和第 5 节对工程师的要求完全一样。

## 3. 命令（每次改动后都要跑）

```bash
python tools/build_site.py       # 重建页面 + data.js
python tools/build_docs.py       # 重建 90 个 PDF（产品数据变了才需要）
python tools/build_dist.py       # 生产构建 -> dist/
python tools/check.py            # 质量门禁，必须 PASS
python server/dev_server.py 8080 # 本地全栈（静态 + /api/*）
```

**收尾三件套**：`build_dist.py` → `check.py` 通过 → 截图核对（1440 与 390 两档）。
缺任何一步都不算完成。

## 4. 目录职责

```
content/      内容源（YAML），后台编辑对象；tools/content.py 在此之上做加载
content/products/  一个产品一个文件，顺序由 order 字段决定，目录号由 sku_code 冻结
content/applications|faq|articles/  同样一文件一条，order 决定顺序
website/      开发目录（可读、未压缩）——只改这里，不改 dist/
  admin/      后台编辑界面（Decap），仅授权后可见，noindex，不进 sitemap
dist/         构建产物，由脚本生成，禁止手改、禁止提交
tools/        content.py（加载器）/ build_site.py / build_docs.py / build_dist.py / check.py
server/       worker.js（生产 API）/ dev_server.py（本地）/ wrangler.toml / oauth-worker/
.github/      CI：构建 + 门禁 + 发布
docs/         90 个 PDF，由 build_docs.py 生成，禁止手改
versions/     版本快照，只增不改
```

## 5. 硬规则

1. **只手改 `website/`、`tools/`、`content/`**（CI 与 OAuth worker 见 2.1）。`dist/`、`docs/*.pdf`
   都是产物，改了会被下次构建覆盖。
2. **内容只在 `content/*.yaml` 改**。`tools/content.py` 只做加载与形态归一（specs → 有序映射、
   steps → 元组、count → 计算值），不存数据。不要在 HTML 里硬编码产品、价格、规格。
3. **数量不写死**。SKU 数用 `NSKU = len(PRODUCTS)`；应用页上的产品数由产品列表计算，不手写 `count`。
   页面里不出现 "42" 这样的字面量。
4. **设计令牌不新增**。颜色只用 `--brand/--accent/--sky/--ink/--muted/--line/--mist` 系列；
   字号只用现有 `clamp()` 阶梯；间距只用 4 的倍数。要加新令牌先说明理由。
5. **不编造事实**。规格、纯度、内毒素、DMF 文号、客户数、市占率，一个都不许自己写。
   缺数据就留 `TODO(content):` 注释并在回复里列出。
6. **英文文案规则**：不用最高级形容词（best/leading/world-class），不写"我们还没做到 X"
   （自我披露能力缺口），目录叫 Products 不叫 Tools。
7. **AI 只做 P1**：检索问答。不实现实验设计建议、不做语音、不做数字人。
8. **表单失败必须有兜底**：任何提交失败都要给出 mailto，不允许只显示"请稍后再试"。
9. **`prefers-reduced-motion` 必须被尊重**：新增动画都要加进已有的 reduce 块。
10. **不提交 `dist/`、`server/outbox/`、`.venv/`、`shots/`**。

## 6. 改设计之前

先读 `DESIGN-LANGUAGE.md`。里面写死了：断点（1320/1180/1120/1100/860/560）、
缓动 `cubic-bezier(.22,.61,.36,1)`、卡片层级、产品线分色（#2A4299 / #1B7FA8 / #574CB0 / #2F8FD0）。
**不要"顺手优化"视觉**。要改视觉，先给出改动清单和影响页面，等确认。

## 7. 完成定义（Definition of Done）

一个任务算完成，必须同时满足：

- [ ] `python tools/build_dist.py` 无报错
- [ ] `python tools/check.py` 输出 PASS
- [ ] 改动页面在 1440px 与 390px 截图核对过
- [ ] 新增/修改的文案符合第 5 节规则
- [ ] 回复里说明：改了哪些文件、为什么、还有什么没做

## 8. 回复格式

- 先给结论，再给细节；不写"好的，我来帮你…"
- 列改动文件时给路径，不给"相关文件"
- 遇到需要客户提供的信息，集中列一次，不要边做边问

## 9. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.1 | 2026-11-03 | 批准后台内容管理：新增 2.1 例外条款；内容源迁至 `content/*.yaml`；应用页产品数改为计算值；目录职责补 `content/`、`website/admin/`、`.github/` |
| v1.0 | — | 初版 |

