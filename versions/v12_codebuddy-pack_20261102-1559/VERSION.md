# v12 — CodeBuddy 开发方案与提示词包

## 新增
- `CODEBUDDY.md`（仓库根，代理常驻约束：技术栈、命令、10 条硬规则、完成定义）
- `README.md`（仓库索引与快速开始）
- `codebuddy/README.md`：协作协议（一轮一个提示词、上下文预算、7 种失败模式与纠法）
- `codebuddy/prompts/00–08`：9 份分阶段提示词，每份含 目标/前置/任务/约束/验收/交付
- `tools/check.py`：质量门禁（链接、meta 唯一性、canonical、JSON-LD、h1、产物完整性、图片体积）

## 提示词序列
00 初始化 → 01 内容 YAML 化 → 02 构建加固（srcset/打印/报告）→ 03 表单生产化
（Turnstile/限流/CRM/回执）→ 04 AI P1 RAG（语料/混合检索/引用/评测集）
→ 05 COA 批次索引 → 06 部署监控 → 07 内容替换 → 08 上线验收

## 实测
`tools/check.py` 对 dist 与 website 均 PASS（12 页 / 48 项硬检查）

## 回滚
覆盖回对应目录即可；codebuddy/ 为文档，删除不影响站点。
