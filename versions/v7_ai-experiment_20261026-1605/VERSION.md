# v7 — AI 文案改为「辅助完成实验」

## 起因
原先把 AI 写成了问答/检索助手（"Ask me about a tool, a DMF reference"），
实际定位是 AI 辅助完成生物实验，典型场景是表达设计。

## 参考
- DBTL（Design-Build-Test-Learn）闭环是行业标准表述
- 行业痛点：AI 可生成 500–5000 条候选序列，但表达验证跟不上
- 表达设计的具体变量：密码子优化（宿主偏好、mRNA 二级结构、稀有密码子）、
  信号肽、标签位置、载体架构、宿主（E. coli / HEK293 / CHO）、诱导条件、可溶性预测

## 改动
- 首页 AI 区块：标题改 "AI designs the experiment. The bench proves it."
  四格改为 Design / Predict / Test / Learn
- 四层栈 02 层：Design and optimisation models → Expression design models
- 闭环：Define-Design-Validate-Scale → Design-Build-Test-Learn
- 平台页 02 层详情重写（密码子、信号肽、可溶性预测）
- AI 客服：问候语、快捷问题、输入框占位、状态行、占位回复全部改为实验设计语境
- 服务页 GMP 表达服务描述加入"构建体由模型设计"
- 设计语言 6.7 增加"定位规则"：AI 文案必须指向可执行实验动作，不指向查询

## 回滚
覆盖回 website/、tools/、DESIGN-LANGUAGE.md。
