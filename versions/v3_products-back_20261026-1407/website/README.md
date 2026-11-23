# T&L Biotechnology — 官网（AI for science 版）

静态站点，10 个页面，2.4 MB，无外部依赖，可直接托管到任意静态服务器。

## 定位

**AI for science · 生命科学工具平台。**

不是「CGT 原料供应商」，而是「用 AI 设计、在自己实验室验证、通过合作网络交付」的工具平台。
DMF / ISO / GMP 从「主张」降级为「验证能力」的证据，不再占据首屏。

叙事主线：**四层栈 + 一个闭环**

| 层 | 内容 | 对客户的价值 |
|---|---|---|
| 01 Data | 批次记录、协议结果、QC 数据 | 下一个项目从测量过的先验出发 |
| 02 Models | 蛋白/抗体设计、配方筛选、协议优化 | 减少从规格到可用试剂的实验轮次 |
| 03 Tools | 41 个 SKU，四大族 | 一次验证，可放大，不用重设计 |
| 04 Lab network | 自有 3,200㎡ + 合作机构 | 通量不再受一栋楼限制 |

闭环：Define → Design → Validate → Scale，第四步回流第一步。

## 页面

| 文件 | 作用 |
|---|---|
| `index.html` | 首页：栈卡片 Hero（含产品缩略图）→ 四层栈 → 闭环 → **产品族大卡 + 精选 6 个 SKU（带图带价）+ 管线胶囊** → 应用分标签 → 自动化路线图 → 产能网络 → 应用科学家 → 数据带 → 资源 → CTA |
| `platform.html` | 平台页：四层逐层展开 + 闭环 + **「我们不是什么」边界声明** |
| `services.html` | 服务：定制开发 / **实验室自动化路线图** / **产能网络** / 应用科学家 |
| `products.html` | 工具目录 + **在研管线**（核酸提取、细胞培养、蛋白纯化、抗体发现） |
| `applications.html` | 6 个细胞类型工作流 |
| `quality.html` | 质量与法规（DMF 表、文件、可追溯） |
| `resources.html` | COA 查询、技术文库、FAQ |
| `about.html` | 公司：从试剂商到平台的转型叙事 |
| `contact.html` | 询价表单、办公室 |

## 关于「自动化」的写法

刻意采用**路线图**而非**现状宣称**：

- Today：Expert-led, manual（每项目一位署名科学家，1–5 L，7–10 天）
- Next 12 months：Semi-automated（液体处理 + 数字作业指导，产能约 3×）
- 2027+：High-throughput（多站点调度，订单到结果 SLA）

融资叙事需要「未来能力」，但客户尽调会打假。用「已发布的时间表 + 明确的能力边界」同时满足两边。

## 关于「分包整合」的写法

对外表述为 **capacity network**，四步：Order intake → Qualification → Routing → Return。
配套「合作机构准入四条」：方法契合、数据格式、质量体系、交付窗口。

**未在公开站点点名任何具体机构。** 中科院 / 军科院 / 高校实验室属于内部资源规划，
公开署名需要对方书面授权，尤其涉军单位有额外合规要求。当前文案用
"academic core facilities and specialist laboratories" 概括。

## 待确认（影响最终文案）

1. **品牌名**：是否继续用 T&L Biotechnology？若要做独立 AI 平台品牌，需要新名字与域名。
2. **专家署名**：庆丰的英文名、头衔、是否可公开照片。当前是 "Application Science Lead"
   + "Backgrounds at Miltenyi Biotec and STEMCELL Technologies" 的匿名写法。
3. **合作机构**：是否有已获授权可公开点名的机构。
4. **AI 能力边界**：目前写的「模型提议候选、科学家决策」是保守表述，如实际已有模型/数据平台，
   可以写得更实（例如具体模型类型、数据量级）。
5. **融资口径**：路线图时间点（12 个月 / 2027）是否与 BP 一致。

## 设计说明

- 品牌色取自 logo：`#2A4299` / `#3289CA` / `#5FB7E8`
- 字体 Inter（自托管，无外链）
- 四层栈配色：`#5FB7E8` → `#2F8FD0` → `#2A4299` → `#1D3170`，由浅到深对应由内到外
- 区块序号 01–08，编辑式节奏
- 响应式断点 1100 / 860 / 560

## 产品展示位置

| 位置 | 内容 |
|---|---|
| 首页 Hero | 栈卡片底部 4 个产品缩略图 + 「+38 more」 |
| 首页 Tools | 4 张产品族大卡（带图、族色、SKU 数）+ 精选 6 个 SKU（图 / 名称 / 起价 / 规格） |
| 首页 Applications | 6 个应用面板内各 6 个产品小卡 |
| `products.html` | 全部 42 个 SKU，筛选 + 排序 + 搜索 |
| `product.html` | 单个 SKU 详情，`?p=<slug>` |

SKU 数量由 `NSKU = len(PRODUCTS)` 统一计算，改 `content.py` 后自动同步。

## 修改方式

内容在 `../tools/content.py`（POSITIONING / STACK / LOOP / PORTFOLIO_NOW / PORTFOLIO_NEXT /
AUTOMATION / NETWORK / EXPERT / PRODUCTS / SERVICES / FAQ / NAV），
结构在 `../tools/build_site.py`。

```bash
python ../tools/build_site.py
```

`assets/js/data.js` 由构建脚本生成，不要手改。

## 仍需处理的工程项

- 规格参数为占位模板，需按真实 COA 核对
- 部分产品图为同系列替代图
- 表单未接后端
- 页脚 Privacy / Terms 为占位链接
