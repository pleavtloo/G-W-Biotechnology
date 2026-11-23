# T&L Biotechnology — 官网（AI for science 版）

静态站点，11 个业务页 + 2 个设计评审页，3.5 MB，无外部依赖，可直接托管到任意静态服务器。

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
| `index.html` | 首页（v1 结构 + 新增 AI 区块）：产品 Hero → 信任条 → 五步工艺流 → 四产品族 → **AI 能力带（四层栈）** → 应用分标签 → 质量深色区 → 定制服务 → 资源 → CTA |
| `platform.html` | 平台页：四层逐层展开 + 闭环 + **「我们不是什么」边界声明** |
| `services.html` | 服务：定制开发 / **实验室自动化路线图** / **产能网络** / 应用科学家 |
| `products.html` | 工具目录 + **在研管线**（核酸提取、细胞培养、蛋白纯化、抗体发现） |
| `applications.html` | 6 个细胞类型工作流 |
| `quality.html` | 质量与法规（DMF 表、文件、可追溯） |
| `resources.html` | COA 查询、**文档库（42 个 SKU 的 Datasheet / COA / SDS）**、技术文库、FAQ |
| `about.html` | 公司：从试剂商到平台的转型叙事 |
| `partners.html` | 渠道合作：分销 / OEM / 学术转介三种模式 + 准入条件 + 申请表 |
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

## 首页版本说明

首页保持 v1 结构不变，AI 能力以**追加区块**的方式插入（第 03 节，位于产品族与应用之间），
没有改写原有叙事。完整平台叙事在 `platform.html`。

## AI 入口（已接入全站）

右下角悬浮按钮 + 对话面板，**10 个页面全部生效**（由 `build_site.py` 的 `footer()` 统一注入）。

- 形象：`assets/img/avatar/avatar-b1.jpg`（柔光生物影像）
- 交互：点击展开、ESC 关闭、快捷问题填充、数字人视图切换（右上角展开图标）
- 上下文：在 `product.html?p=<slug>` 打开时，问候语自动带上产品名
- 移动端：≤560px 变为底部全宽抽屉，按钮缩为 46px 头像
- 定位：**AI 辅助完成实验**（表达设计 / 宿主选择 / 筛选矩阵），不是站内搜索
- 演示态：输入框提交只返回占位回复，**未接后端**

要换形象，改 `tools/build_site.py` 里 widget 模板的 3 处 `avatar-b1.jpg` 路径即可。

## 设计稿（非线上页面）

`design-ai-entry.html` — AI 客服入口 + 虚拟数字人的设计评审页，**不参与导航、不要上线**。
`design-avatar.html` — 数字人形象三版对比（写实 / 柔光生物影像 / 极简光带），含 72/38/32/24px 真实尺寸与界面内预览。
包含：可交互原型（点击右下角按钮展开）、三种状态、数字人形象三方向、四个入口位置、AI 应答红线、分期落地建议。

评审地址：`/design-ai-entry.html`（深链 `#open` 面板展开 / `#presence` 数字人模式）、`/design-avatar.html`。

数字人形象素材在 `assets/img/avatar/`：`avatar-a`（写实）、`avatar-b1`（柔光生物影像，当前采用）、
`avatar-b2`（极简光带）、`avatar-b0`（已弃用的线框版）。

上线前删除此文件，或移到独立的设计评审环境。

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
| `product.html` | 单个 SKU 详情，`?p=<slug>`，含 Documents 条（Datasheet / COA / SDS 直接下载） |
| `resources.html#docs` | 文档库：4 张共享文件卡 + 42 行产品表（每行 3 个下载链接） |

SKU 数量由 `NSKU = len(PRODUCTS)` 统一计算，改 `content.py` 后自动同步。

## 文档下载（真实 PDF）

`docs/` 下 90 个 PDF，由 `tools/build_docs.py` 用 fpdf2 生成：

| 文件 | 数量 | 内容 |
|---|---|---|
| `datasheet-<slug>.pdf` | 42 | 2 页：描述 / 订购表 / 规格 / 特性 / 使用与保存 / 兼容性 / 修订记录 |
| `coa-<slug>.pdf` | 42 | 1 页：批次号、检验项、方法、标准、结果、放行声明（代表性文件） |
| `sds-<cat>.pdf` | 4 | 16 节标准 SDS，按产品族 |
| `dmf-summary.pdf` | 1 | 两份 Type II DMF 的引用方式与边界 |
| `quality-overview.pdf` | 1 | 质量体系范围、受控内容、客户可得文件、审计 |

```bash
python ../tools/build_docs.py     # 重新生成全部文档
```

改 `content.py` 的产品后必须重跑，否则文档与页面不同步。
订单号规则 `TL-<族码>-<序号>`，批次号由 slug 哈希稳定生成（同一 SKU 每次生成相同批次号）。

## 修改方式

内容在 `../tools/content.py`（POSITIONING / STACK / LOOP / PORTFOLIO_NOW / PORTFOLIO_NEXT /
AUTOMATION / NETWORK / EXPERT / PRODUCTS / SERVICES / FAQ / NAV），
结构在 `../tools/build_site.py`。

```bash
python ../tools/build_site.py     # 页面 + data.js
python ../tools/build_docs.py     # 90 个 PDF（产品改动后要重跑）
```

`assets/js/data.js` 由构建脚本生成，不要手改。

## 仍需处理的工程项

- 规格参数为占位模板，需按真实 COA 核对
- PDF 文档为演示生成件，需替换为质量部门签发的正式版本（含真实批次与签字）
- 部分产品图为同系列替代图
- 表单未接后端
- 页脚 Privacy / Terms 为占位链接
