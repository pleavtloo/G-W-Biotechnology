# 用 CodeBuddy 开发这个站点

一套可直接照做的协作方案：仓库怎么准备、每轮怎么提、怎么验收、出错怎么纠。

---

## 0. 先理解一件事

CodeBuddy 不是"一句话生成网站"的工具。它能写出合格的代码，但**不知道你的业务约束**——
比如"不许编造内毒素数值""价格必须公开""AI 只做检索不做建议"。

所以这套方案的核心不是提示词写得多漂亮，而是：

```
CODEBUDDY.md（常驻约束）  +  分阶段提示词（一次一件事）  +  check.py（可执行的验收）
```

三者缺一不可。少了第一个，它会自由发挥；少了第二个，它会一次改十个文件；
少了第三个，它说"完成了"你没法验证。

---

## 1. 仓库准备（10 分钟）

```bash
# 1) 把 CODEBUDDY.md 放到仓库根目录（CodeBuddy 会自动读取）
cp codebuddy/CODEBUDDY.md ./CODEBUDDY.md

# 2) 建 .gitignore
cat > .gitignore <<'EOF'
.venv/
dist/
shots/
server/outbox/
server/.dev.vars
__pycache__/
*.pyc
.DS_Store
EOF

# 3) 首次提交（只提交源码，不提交产物）
git init
git add .
git commit -m "baseline: design + build pipeline"

# 4) 确认基线是绿的
python tools/build_site.py
python tools/build_dist.py
python tools/check.py        # 必须 PASS
```

**基线必须是 PASS 才能开始。** 如果一开始就是红的，后面所有报错都分不清是新问题还是旧问题。

---

## 2. 每轮怎么提（固定套路）

不要一次把九个 prompt 全贴进去。**一轮一个**，按编号顺序。

每次会话开头先说这句话：

> 先读 `CODEBUDDY.md`。然后读 `codebuddy/prompts/03-forms-production.md`。
> 复述你要做的改动清单和涉及的文件，等我确认后再动手。

这三句话的作用：
1. 强制它加载约束（否则它会按通用最佳实践改你的项目）
2. 强制它先出计划（否则它直接开始改 15 个文件）
3. 给你一次纠偏机会（"等一下，第 3 条不该动 CSS"）

确认后让它做，做完跑：

```bash
python tools/build_dist.py && python tools/check.py
```

**PASS 才算完。** 不 PASS 就把报错原文贴回去，不要自己总结成"有个小问题"。

---

## 3. 九个阶段

| # | 提示词 | 产出 | 依赖 |
|---|---|---|---|
| 00 | `00-bootstrap.md` | 仓库骨架、命令跑通、基线绿 | — |
| 01 | `01-content-model.md` | `content.py` → YAML + 校验 | 00 |
| 02 | `02-build-hardening.md` | srcset、打印样式、构建报告 | 01 |
| 03 | `03-forms-production.md` | Turnstile、发信、CRM、限流 | 00（可与 02 并行） |
| 04 | `04-ai-rag-p1.md` | 知识库、检索、带引用回答 | 01 |
| 05 | `05-docs-coa.md` | COA 索引、上传、版本管理 | 03 |
| 06 | `06-deploy-monitor.md` | Cloudflare 上线、CI、告警 | 03 |
| 07 | `07-content-swap.md` | 真实规格/图片/专家替换 | **客户给数据后** |
| 08 | `08-launch-acceptance.md` | 全量验收、go/no-go | 全部 |

**关键路径是 07，不是代码。** 01–06 可以在内容未定时全部完成，07 必须等客户。

---

## 4. 上下文预算（别让它读太多）

| 文件 | 何时读 |
|---|---|
| `CODEBUDDY.md` | 每轮必读（自动） |
| `DESIGN-LANGUAGE.md` | 只在动视觉时读 |
| `BUILD-PLAN.md` | 只在规划时读，写代码时不用 |
| `tools/build_site.py` | 按需读函数，不要整文件塞进去（2000+ 行） |
| `website/*.html` | **不要读**。是产物，读它会让它以为要手改 HTML |

最后一条最容易犯。一定要明确说："`website/*.html` 是构建产物，不要直接编辑。"

---

## 5. 常见失败模式与纠法

| 症状 | 原因 | 纠法 |
|---|---|---|
| 它开始改 `dist/` 或 `website/*.html` | 不知道那是产物 | "停。`dist/` 与 `website/*.html` 是 `build_site.py` 的产物，改 `tools/` 或 `content.py`" |
| 它自己编了规格数值 | 缺数据时倾向于"补全" | "规格只能来自 `content.py`，缺的留 `TODO(content):`，不要推断" |
| 它顺手重构了 CSS | 默认行为是"改善代码" | "不要动样式。除非我在本轮的改动清单里明确列出" |
| 它一次改了 12 个文件 | 任务颗粒太大 | 拆：先改生成器，再改内容，分两次 |
| `check.py` 红了但它说"应该没问题" | 没跑验收 | "贴出 `python tools/check.py` 的完整输出" |
| 它引入了 Tailwind / React | 通用最佳实践覆盖了项目约束 | "技术栈见 CODEBUDDY.md 第 2 节，不引入框架" |
| 它把设计评审页也改了 | 不知道那两个要删 | "`design-*.html` 上线前删除，不要维护" |

---

## 6. 三条不可省的验收

```bash
python tools/check.py           # 硬检查：链接、meta、JSON-LD、h1、产物完整性
```

```bash
python server/dev_server.py 8080
# 打开 /contact.html 真填一次表单，看是否落 server/outbox/
```

```bash
# 截图两档，肉眼过一遍
# 1440x900 与 390x844
```

自动化能查结构，查不出"看起来不对"。**每轮至少看一眼截图。**

---

## 7. 提交节奏

一个 prompt 一个 commit，message 写清"改了什么、为什么"：

```
feat(forms): 接 Turnstile + Resend，失败态给 mailto 兜底
fix(build): srcset 生成时忽略 1x 图，避免重复下载
content(specs): 替换 42 个 SKU 的纯度与内毒素（QA 2026-11 版）
```

不要一个 commit 混三件事——出问题时 `git bisect` 会救你。

---

## 8. 交接给客户时给什么

- `dist/` 压缩包（或 Cloudflare Pages 项目权限）
- `CODEBUDDY.md` + `DESIGN-LANGUAGE.md`（后续维护者读这两份就够）
- `server/README.md`（环境变量、发信域配置）
- `BUILD-PLAN.md` 第 9 节「上线前必须删掉的东西」

最后一条最容易漏：**设计评审页、演示 PDF、占位隐私政策**，上线前必须清。
