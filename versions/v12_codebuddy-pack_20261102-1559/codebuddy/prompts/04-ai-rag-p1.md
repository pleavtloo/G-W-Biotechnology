# P04 · AI 客服 P1：检索问答（带引用、无源不答）

**目标**：把 `/api/chat` 从 501 变成真正能答"有什么、在哪、什么规格、DMF 怎么说"的检索问答。

**前置**：P01（内容 YAML 化）。P03 不必须，但上线前要有。

**先读**：`CODEBUDDY.md`、`tools/content.py` 或 `content/*.yaml`、`server/worker.js`、
`website/assets/js/main.js` 里的 AI widget 段

---

## 范围（写死，不要扩）

| 能答 | 不能答 |
|---|---|
| 有哪些产品、某个产品什么规格 | 「我该选哪个」（设计建议 → 转人工） |
| 某个文档在哪、怎么下载 | 临床用法、给药方案、法规结论 |
| DMF 是什么、怎么引用 | 价格谈判、交期承诺 |
| 某个应用的推荐产品组合 | 竞品对比评价 |

**越界即转人工。** 这不是能力不足，是合规要求：生命科学场景里编一个内毒素数值，
比说"我不知道"严重得多。

---

## 任务

### 1. 语料构建 `tools/build_corpus.py`

输出 `data/corpus.jsonl`，每行一个 chunk：

```json
{"id":"p:actsep-cd3-cd28:specs","source":"products.yaml","title":"ActSep® CD3/CD28 — specifications",
 "url":"/product.html?p=actsep-cd3-cd28","text":"Target: Human CD3+ T cells. Bead size: ~4.5 µm. ..."}
```

切分规则：
- 每个 SKU 切成 2–3 块：`desc`（描述）/ `specs`（规格表，一行一条）/ `docs`（文档清单）
- 每个 FAQ 一条
- 每个应用一条
- 每个服务一条
- 90 份 PDF 抽文本（用 `pymupdf`），按小节切，每块 ≤ 800 字符

每条 chunk 必须带 `url`——回答里的引用就靠它。

### 2. 检索

- 关键词：BM25 或简单的字段加权（产品名 > 规格 > 描述）
- 向量：`env.CHAT_API_URL` 同源的 embeddings 端点（OpenAI 兼容 `/embeddings`）
- **混合排序**：`score = 0.6 * 向量相似度 + 0.4 * 关键词得分`
- 取 top 5，**阈值 0.35**：全部低于阈值时**不调用 LLM**，直接返回转人工

向量存哪：先存 `data/embeddings.json`（约 200 条 × 1536 维，约 1.2 MB），
上传到 Worker 用 `import` 或 KV。数据量在这个量级不需要向量数据库。

### 3. 回答生成

系统提示词（写进 `server/prompts/system.md`，构建时内联）：

```
You answer questions about T&L Biotechnology's life science tools using ONLY the
provided context. Rules:
- If the context does not contain the answer, say so and offer a human handoff.
- Never invent specifications, concentrations, regulatory status or prices.
- Cite sources as [1], [2] matching the provided context order.
- Keep answers under 120 words. Prefer tables for specifications.
- For questions about which product to choose, clinical use, or regulatory conclusions,
  decline and hand off to an application scientist.
```

返回结构：

```json
{ "ok": true,
  "reply": "MaxSortin® CD3 uses 50 nm nanobeads ... [1]",
  "sources": [{"n":1,"title":"MaxSortin CD3 — specs","url":"/product.html?p=maxsortin-cd3"}] }
```

### 4. 前端接线

- `main.js` 的提交处理：POST `/api/chat`，`messages` 带上最近 4 轮
- 渲染：气泡 + 引用列表（可点，链到产品页或 PDF）
- 无引用时**不显示**任何"来源"区块，但回答里必须明确说"我不确定，建议问科学家"
- 失败/501：显示"AI 暂不可用，点这里联系应用科学家"
- 保留底部的 `AI-generated · verify before use`

### 5. 评测集（必须做）

`data/eval.jsonl`，30 条，格式：

```json
{"q":"What is the endotoxin spec for IL-7?","must_contain":["EU/µg"],"must_cite":true}
{"q":"Which product for NK expansion?","expect":"handoff"}
{"q":"Do you ship to Germany?","must_contain":["ship"],"must_cite":false}
```

`tools/eval_chat.py` 跑全量，输出通过率。**上线门槛：≥ 85%，且"编造率"必须为 0**
（编造率 = 回答里出现了语料中没有的数字/文号）。

### 6. 日志与合规

- 每次对话记：`{evt:"chat", q_hash, retrieved_ids, answered:bool, cited:bool, ms}`
- **不记完整问题文本**（PII），只记哈希与命中 id
- 保留 6 个月（合规要求），用 KV 或 R2，过期自动清理

## 约束

- 不做语音、不做数字人、不做实验设计建议
- 不引入向量数据库、不引入 LangChain 之类框架，直接用 `fetch` + 自己写的检索
- 语料里**不许出现** `content/` 之外的事实
- 回答长度上限 120 词，超出截断

## 验收

```bash
python tools/build_corpus.py            # 输出 chunk 数与总量
python tools/eval_chat.py               # 通过率 >= 85%，编造率 0
python server/dev_server.py 8080
# 打开任意页 -> 点右下角 -> 问 "What is the endotoxin spec for IL-7?"
# 期望：给出数值 + 引用链接，数值与 products.yaml 完全一致
```

## 交付

- `tools/build_corpus.py`、`tools/eval_chat.py`
- `data/corpus.jsonl`、`data/eval.jsonl`、`data/embeddings.json`
- `server/prompts/system.md`
- `server/worker.js` 的 `/api/chat` 实现
- `main.js` 的对话渲染与引用
- 评测报告（通过率、失败样例）

## 备注

评测集里的"必须包含"字段要从 `products.yaml` **程序化生成**，不要手写数字——
手写的期望值会跟着内容一起过期。
