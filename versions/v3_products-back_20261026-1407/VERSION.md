# v3 — 首页产品展示恢复

在 v2（AI for science 定位）基础上，把产品重新放回首页视觉主体。

## 改动
- 首页 Tools 区块：文字列表 → 4 张产品族大卡（带图）+ 精选 6 个 SKU（图/名/起价）+ 管线胶囊
- Hero 栈卡片底部新增 4 个产品缩略图 + "+38 more"
- 全站 SKU 数量统一为 42，改由 `NSKU = len(PRODUCTS)` 计算
- 新增组件：`.feat / .fcard / .pipechips / .stackcard__thumbs`

## 精选 SKU
ActSep® CD3/CD28 · MaxSortin® CD3 · Anti-Human CD3 mAb · IL-2 · IL-7 · AMMS® NK Kit 3.0

## 回滚
覆盖回根目录 `website/` 与 `tools/`。
