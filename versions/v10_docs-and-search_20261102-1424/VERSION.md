# v10 — 文档下载 + 醒目搜索 + 第三条边界

## 1. 产品资料下载（真实 PDF）
新增 `tools/build_docs.py`（fpdf2），生成 90 个 PDF 到 `website/docs/`：
- `datasheet-<slug>.pdf` × 42（2 页：描述 / 订购 / 规格 / 特性 / 使用保存 / 兼容性 / 修订记录）
- `coa-<slug>.pdf` × 42（批次号、检验项、方法、标准、结果、放行声明）
- `sds-<cat>.pdf` × 4（16 节）
- `dmf-summary.pdf`、`quality-overview.pdf`

三处入口：
- 产品卡图右下 `.gcard__dl` 角标（直接下载 datasheet）
- 卡片 COA 按钮 → `docs/coa-<slug>.pdf`
- 详情页购买框下 `.pdp__docs` 条 + Documentation 标签页
- `resources.html#docs` 文档库：4 张共享文件卡 + 42 行表格

## 2. 搜索入口醒目化
- 头部图标按钮 → `.search-trigger` 字段式按钮（浅蓝底 + 品牌蓝描边 + 「Search 42 products」+ ⌘K）
- 断点：>1320 完整 / 1180–1320 收窄无 ⌘K / ≤1180 图标 / ≤860 抽屉顶部 `.mm-search`
- 搜索浮层加空状态（热门词 + 4 个品类带 SKU 数）、命中数、结果带族与起价、「See all N」
- 匹配扩展到规格值；`products.html?q=` 深链过滤
- 导航在 1120px 起压缩间距并隐藏品牌副标，修复 1024 下 Quote 按钮溢出

## 3. 平台页补第三条边界
"We are not an instrument company." — 不卖硬件，为现有平台设计实验，必要时路由产能。三栏版式恢复平衡。

## 回滚
覆盖回 `website/`、`tools/`、`DESIGN-LANGUAGE.md`。docs 为生成物，可整目录删除后重跑。
