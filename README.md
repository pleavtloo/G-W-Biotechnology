# T&L Biotechnology — 官网工程

静态站点 + 边缘 API。页面由 Python 生成，无前端框架。

## 快速开始

```bash
python tools/build_site.py       # 生成页面 -> website/
python tools/build_dist.py       # 生产构建 -> dist/
python tools/check.py            # 质量门禁（必须 PASS）
python server/dev_server.py 8080 # 本地全栈：静态站 + /api/*
```

首次运行需要：`pip install fpdf2 pyyaml pymupdf`

## 文档地图

| 文件 | 什么时候读 |
|---|---|
| `CODEBUDDY.md` | 改任何代码之前（约束与完成定义） |
| `DESIGN-LANGUAGE.md` | 动视觉之前（令牌、断点、组件规格） |
| `BUILD-PLAN.md` | 规划与排期（技术路线、工作流、成本、风险） |
| `codebuddy/README.md` | 用 CodeBuddy 开发时的协作协议 |
| `codebuddy/prompts/` | 分阶段提示词，按编号顺序执行 |
| `server/README.md` | 部署 API、配置环境变量 |
| `website/README.md` | 页面清单、内容维护方式 |

## 目录

```
content/    （P01 后）内容 YAML，唯一真相
tools/      content.py · build_site.py · build_docs.py · build_dist.py · check.py
website/    开发目录，页面模板输出
dist/       构建产物，禁止手改、禁止提交
server/     worker.js（生产）· dev_server.py（本地）
docs/       90 个 PDF，构建生成
versions/   版本快照
codebuddy/  开发方案与提示词
```

## 当前状态

- 设计：定稿（11 个业务页 + 404）
- 构建：`dist/` 可部署，SEO / sitemap / headers 齐全
- 表单：本地端到端可用，生产需部署 worker
- AI：仅外壳，`/api/chat` 返回 501（待 P04）
- 内容：规格与 PDF 为占位，待客户数据（P07）
