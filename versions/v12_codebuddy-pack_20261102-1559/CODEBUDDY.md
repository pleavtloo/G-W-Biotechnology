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
website/      开发目录（可读、未压缩）——只改这里，不改 dist/
dist/         构建产物，由脚本生成，禁止手改、禁止提交
tools/        content.py（唯一内容源）/ build_site.py / build_docs.py / build_dist.py / check.py
server/       worker.js（生产 API）/ dev_server.py（本地）/ wrangler.toml
docs/         90 个 PDF，由 build_docs.py 生成，禁止手改
versions/     版本快照，只增不改
```

## 5. 硬规则

1. **只改 `website/` 与 `tools/`**。`dist/`、`docs/*.pdf` 都是产物，改了会被下次构建覆盖。
2. **内容只在 `tools/content.py` 改**，不要在 HTML 里硬编码产品、价格、规格。
3. **数量不写死**。SKU 数用 `NSKU = len(PRODUCTS)`，页面里不出现 "42" 这样的字面量。
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
