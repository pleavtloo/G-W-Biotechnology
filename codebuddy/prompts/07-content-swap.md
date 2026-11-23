# P07 · 内容替换：占位数据 → 真实数据

**目标**：把站点从"演示件"变成"可以给客户和监管看的东西"。

**前置**：客户已交付规格表、图片、专家授权、COA 样例。**没有这些不要开始这一步。**

**先读**：`CODEBUDDY.md`、`content/products.yaml`、`tools/build_docs.py`

---

## 这一步的性质

其他阶段是写代码，这一步是**核对事实**。写代码可以自己判断，核对事实不行——
任何数字都必须来自客户文件，不允许推断、不允许"看起来合理就填"。

---

## 任务

### 1. 规格替换（42 个 SKU）

- 从客户给的 Excel 导入 `content/products.yaml`（写 `tools/import_specs.py`，一次性脚本）
- 字段映射：客户表头 → YAML 键，映射表写在脚本里，便于复核
- **逐条比对**：导入后生成 `reports/specs-diff.md`，列出每个 SKU 的
  `旧值 → 新值`，供 QA 签字
- 缺失字段留空并汇总到 `reports/specs-missing.md`，**不要填默认值**

### 2. 价格

- 确认公开价与内部价的一致性（公开的是 list price）
- `priceValidUntil` 改成真实有效期（当前写死 2027-12-31）
- 如果客户要求"询价"，把 `price` 置空，页面自动降级为 `Price on request`（已实现）

### 3. 图片

- 每 SKU 白底图 ≥ 2000px，命名 `<slug>.webp` 与 `<slug>-tile.webp`
- 若仍用替代图，在 `reports/images.md` 标注哪些是替代、原图待补
- **不要用生成图冒充产品图**

### 4. 专家与合作机构

- 专家：英文名、头衔、照片、前雇主可署名范围——**必须有书面授权**
- 合作机构：默认不点名（当前文案已如此）。若客户要写，需对方授权函
- 授权文件放 `legal/`，不进站点

### 5. 文档重生成

```bash
python tools/build_docs.py     # 90 个 PDF 用新规格重生成
python tools/check.py
```

PDF 里 `Specifications` 表必须与新 YAML 一致（写个脚本抽查 5 个 SKU 比对文本）。

### 6. 上线前清理清单

- [ ] `design-ai-entry.html`、`design-avatar.html` 删除
- [ ] `docs/coa-*.pdf` 换成 `coa-sample-*.pdf` + `Sample only` 标签（或 P05 的真实索引）
- [ ] 页脚 Privacy / Terms 换成真实页面
- [ ] 所有 `TODO(content):` 注释清零
- [ ] AI 面板里的演示话术替换为真实能力描述

## 约束

- **不推断任何数值**。缺就留空并报告。
- 不改页面结构，只改内容。
- 每次批量导入后必须重建 + `check.py` + 抽 3 个页面截图。

## 验收

```bash
python tools/import_specs.py --dry-run   # 先看 diff，不写文件
python tools/import_specs.py
python tools/build_site.py && python tools/build_docs.py && python tools/build_dist.py
python tools/check.py
grep -rn "TODO(content)" content/ tools/ | wc -l    # 期望 0
```

## 交付

- `content/products.yaml` 更新
- `reports/specs-diff.md`（供 QA 签字）
- `reports/specs-missing.md`、`reports/images.md`
- 重生成的 90 个 PDF
- 清理清单的逐条勾选结果

## 备注

这一步最容易出的错是"补全"。看到某个 SKU 缺内毒素指标，本能会想按同类填一个——
**不能填**。缺指标的 SKU 在页面上就不该显示那一行（构建时跳过空字段），
这比显示一个假数字安全得多。
