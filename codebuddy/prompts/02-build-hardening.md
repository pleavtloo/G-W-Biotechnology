# P02 · 构建加固：srcset、打印样式、构建报告

**目标**：把构建从"能出页面"提升到"能交付给客户 IT"。

**前置**：P00。可与 P01 并行，但 P01 之后要做一次 rebase 验证。

**先读**：`CODEBUDDY.md`、`tools/build_dist.py`、`website/assets/css/style.css` 末尾的媒体查询块

---

## 任务

### 1. 响应式图片（srcset）

现在所有 `<img>` 都是单尺寸，Retina 屏偏软。

- 写 `tools/gen_images.py`：读 `assets/img/products/*.webp`，输出三档 `-400/-800/-1200.webp`
  （原图小于目标宽度则跳过，不放大）
- 构建时替换 `<img src>` 为：
  ```html
  <img src="...-800.webp" srcset="...-400.webp 400w, ...-800.webp 800w, ...-1200.webp 1200w"
       sizes="(max-width: 560px) 100vw, (max-width: 1100px) 50vw, 380px" ...>
  ```
- `sizes` 必须按实际布局给，不要一律 `100vw`

### 2. 打印样式

B2B 客户会把规格页打印给采购。

- 在 `style.css` 加 `@media print`：
  - 隐藏：header、footer 导航、AI 悬浮按钮、搜索、面包屑、CTA 条
  - 展开：所有 `display:none` 的 tab 面板（规格、文档）改成全部可见
  - 链接：`a[href^="http"]::after { content: " (" attr(href) ")" }`
  - 分页：`h2, h3 { break-after: avoid }`，`.gcard { break-inside: avoid }`
- 产品详情页打印时，页眉要有产品名 + 订单号 + 日期

### 3. 构建报告

`build_dist.py` 结束时输出结构化摘要（现在只有体积）：

```
pages        12
images       84 (+168 generated)
largest page products.html  74.2 KB
largest asset assets/img/products/xxx.webp  32 KB
total        9.1 MB
slowest      3 warnings
```

并把结果写进 `dist/build-report.json`，供 CI 读取。

### 4. 图片体积门禁

`check.py` 增加一条：单张图片 > 150 KB 报 warn，> 400 KB 报 fail。

## 约束

- 不改变现有视觉。srcset 只换资源，不动布局。
- 打印样式不得影响屏幕渲染（用 `@media print` 隔离，不要覆盖全局）。
- 生成的多尺寸图放 `assets/img/products/`，命名规则 `<slug>-400.webp`，不要建新目录。
- 不引入 sharp/Pillow 之外的工具；Pillow 已在 `.venv`。

## 验收

```bash
python tools/gen_images.py
python tools/build_dist.py
python tools/check.py

# 打印预览：Chrome -> Print -> 存 PDF，检查产品页是否把规格表也打出来了
# 打开 dist/product.html?p=actsep-cd3-cd28 打印预览
```

期望：`check.py` PASS；产品页打印件包含「Specifications」全文；页面 LCP 不劣化。

## 交付

- `tools/gen_images.py`
- `build_dist.py` 的 srcset 改写与报告
- `style.css` 的 `@media print` 块
- `check.py` 新增的图片体积检查
- 一张打印预览截图
