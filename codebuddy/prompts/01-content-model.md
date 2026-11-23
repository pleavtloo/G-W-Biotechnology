# P01 · 内容层抽离：content.py → YAML + 校验

**目标**：把内容从 Python 代码里拿出来，让非工程师也能改，并为将来接 CMS 留出接口。

**前置**：P00 完成，基线 PASS。

**先读**：`CODEBUDDY.md`、`tools/content.py`、`tools/build_site.py` 里的 `main()` 与 `write_data_js()`

---

## 为什么做

现在 42 个 SKU、4 个品类、6 个应用、服务与 FAQ 全写在 `content.py` 里。
改一个产品要碰 Python 语法，市场同事改不了；将来接 CMS 也要先有稳定的数据契约。

## 任务

1. 新建 `content/` 目录，按实体拆文件：

   ```
   content/
     company.yaml        # 名称、地址、电话、DMF 号、site_url
     categories.yaml     # 4 个产品族
     products.yaml       # 42 个 SKU
     applications.yaml   # 6 个应用
     services.yaml
     faq.yaml
     articles.yaml
     positioning.yaml    # POSITIONING / STACK / LOOP / AUTOMATION / NETWORK / EXPERT
   ```

2. 写 `tools/load_content.py`：
   - 读 YAML → 返回与现在**完全一致**的 Python 结构（键名、类型、顺序都不变）
   - 校验必填字段，缺失时给出**可读的错误**：文件、条目、字段名
   - 校验唯一性：`slug` 不重复、`cat` 必须存在于 categories
   - 校验数量：`products` 每个 `cat` 至少有 1 个，总数与 `applications` 里的 `count` 一致

3. `tools/content.py` 改为兼容层：内部调用 loader，对外仍暴露 `PRODUCTS`、`CATEGORIES` 等同名变量。
   **`build_site.py` 与 `build_docs.py` 一行都不用改。**

4. 用脚本从现有 `content.py` 导出初始 YAML，保证导出后重建的页面与现在**逐字节一致**
   （用 `git diff --stat dist/` 验证）。

5. `build_site.py` 里加一条构建时断言：如果 `len(PRODUCTS) != 42`，打印警告但不中断
   （客户可能新增 SKU，不该阻断构建）。

## 约束

- **不改任何文案**。这一步只搬位置，不改内容。文案修订是 P07 的事。
- 不引入除 `PyYAML` 之外的依赖（如果要用，先确认 `.venv` 里有没有）。
- YAML 里保留中文注释说明字段含义，但**值必须是英文**（站点仅英文）。
- 保持 `content.py` 的公开接口不变，否则构建脚本要改。

## 验收

```bash
python tools/build_site.py
python tools/build_docs.py
python tools/build_dist.py
python tools/check.py
git diff --stat dist/            # 应该只有 sitemap 的 lastmod 变化，页面内容不变
```

再验证校验器真的会报错：

```bash
# 故意把某个产品的 slug 改成重复，确认报错信息包含文件名与 slug
python -c "import sys; sys.path.insert(0,'tools'); import load_content; load_content.load()"
```

## 交付

- `content/*.yaml` 全部 8 个文件
- `tools/load_content.py`（含校验与错误信息）
- 改后的 `tools/content.py`（兼容层）
- 证明页面无变化的 `git diff --stat`

## 备注

做完这一步，`products.yaml` 就是**唯一的产品真相**。之后所有"改规格""加 SKU"都只动这一个文件，
再加跑 `build_docs.py` 重生成 PDF。
