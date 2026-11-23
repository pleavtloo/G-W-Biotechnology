# 内容字段契约（Content Schema）

> 状态：已确认（2026-11-03）　　版本：v1.0　　日期：2026-11-03
> 用途：定义 `content/*.yaml` 的字段、类型与校验规则。后台表单、构建脚本、迁移脚本均以此为准。
> 上位文档：`BACKEND-REQUIREMENTS.md`

## 0. 通用约定

| 项 | 约定 |
|---|---|
| 编码 | UTF-8，无 BOM |
| 缩进 | 2 空格，不用 Tab |
| 命名 | 全小写 + 下划线（`image_tile`），与现有 `content.py` 键名保持一致 |
| 顺序 | 数组顺序即页面展示顺序；`specs` 顺序即规格表行序 |
| 只读字段 | `slug`、`id`、`site_url`、`turnstile_sitekey` 后台不可编辑 |
| 图片 | 仓库内相对路径，由构建脚本复制到 `website/assets/img/` |
| 空值 | 用 `null` 或省略，不用空字符串 |
| 事实性数据 | 纯度、内毒素、DMF 文号等必须有来源，禁止占位值 |

**文件根节点是对象。** Decap CMS 只能把文件根当成一个映射来编辑，所以列表统一包在同名
key 下（`products:` / `applications:` / `faq:` / `articles:` / `categories:`），
`site.yaml` 本身就是一个平铺对象。加载器 `tools/content.py::_load(name, key)` 负责取值。
下文各节的示例省略了这层外壳，真实文件长这样：

```yaml
products:
  - slug: actsep-cd3-cd28
    name: ActSep® CD3/CD28 Separation & Activation Beads
```

## 1. 目录结构

```
content/
├── products/           # 42 个 SKU，一文件一条（order 决定顺序，sku_code 冻结编号）
├── applications/       # 6 个应用场景，一文件一条（文件名 = id）
├── faq/                # 常见问题，一文件一条（faq-01 … faq-06）
├── articles/           # 资源页文章卡片，一文件一条（article-01 …）
├── site.yaml           # 公司信息与部署参数（单文件，本来就是一条记录）
└── categories.yaml     # 4 个产品分类（单文件，后台只读）
```

> 所有 `一文件一条` 的目录都由 `order` 字段决定顺序，**不依赖文件名**。

`tools/content.py` 保留为加载器：读取上述文件，暴露同名的 `PRODUCTS` / `APPLICATIONS` /
`FAQ` / `ARTICLES` / `COMPANY` / `CATEGORIES` 变量，使
`build_site.py`、`build_docs.py`、`build_dist.py` 无需修改。

## 2. `products/*.yaml`（一个产品一个文件）

```yaml
# content/products/actsep-cd3-cd28.yaml
order: 1                            # 目录顺序，只读
sku_code: TL-BD-101                 # 冻结的目录号，只读
slug: actsep-cd3-cd28               # 只读
name: ActSep® CD3/CD28 Separation & Activation Beads
cat: beads                          # beads | antibodies | proteins | media
apps: [tcell]                       # tcell | nk | msc | ipsc | hsc | dc
price: 510                          # 数字或 null
sizes: ["1 mL", "2 mL", "5 mL"]     # 至少 1 项，首项为起订规格
blurb: Single-reagent isolation and activation of human CD3⁺ T cells.
desc: >
  ActSep® beads combine anti-human CD3 and CD28 antibodies on a magnetic core.
highlights:
  - FDA DMF filed — DMF 038124
  - Detachable, low-retention bead chemistry
specs:
  - { k: Target,    v: Human CD3⁺ T cells }
  - { k: Bead size, v: ~4.5 µm }
  - { k: Endotoxin, v: ≤ 0.5 EU/mL }
image_tile: assets/img/products/actsep-cd3-cd28-tile.webp   # 必填
image: assets/img/products/actsep-cd3-cd28.webp             # 可空，用于 JSON-LD
shop_product_id: 568                # OpenCart 商品号；为空则只询价
```

> `order` 与 `sku_code` 是**冻结字段**：前者决定目录顺序，后者决定 PDF 上的目录号。
> 两者都不能跟文件顺序或文件名绑定，否则删一个产品会让后面所有编号错位。

| 字段 | 类型 | 必填 | 约束 | 消费方 |
|---|---|---|---|---|
| `slug` | string | 是 | `^[a-z0-9-]+$`，只读；改它 = 断外链 + 改 PDF 名 | URL、图片名、PDF 名 |
| `name` | string | 是 | ≤ 80 字符，保留 ® / ™ | 卡片、详情页、搜索、JSON-LD |
| `cat` | enum | 是 | 必须存在于 `categories.yaml` | 分类筛选、角标 |
| `apps` | string[] | 是 | ≥ 1，元素必须存在于 `applications.yaml` | 应用筛选、应用页关联 |
| `price` | number \| null | 否 | ≥ 0，最多 2 位小数 | `null` 渲染 “Price on request” |
| `sizes` | string[] | 是 | ≥ 1 | 价格后缀、详情页规格选择、PDF |
| `blurb` | string | 是 | ≤ 120 字符（卡片按 58 截断） | 卡片副标题 |
| `desc` | string | 是 | ≤ 1200 字符 | 详情页正文、JSON-LD |
| `highlights` | string[] | 是 | 建议 3 项，2–5 项均可 | 详情页要点 |
| `specs` | object[] | 是 | ≥ 1 组 `{k, v}`，`k` ≤ 24 字符，`v` ≤ 60 字符 | 详情页规格表、PDF 数据表 |
| `image_tile` | path | 是 | 存在性校验，建议 1200×900 WebP | 卡片、搜索、详情缩略图 |
| `image` | path | 否 | 存在性校验 | JSON-LD `image` |
| `shop_product_id` | number \| null | 否 | 必须是 OpenCart 里存在的 `product_id`；为空则页面显示「Request a quote」而非「Buy」 | 购买按钮跳转 |

## 3. `applications.yaml`

```yaml
- id: tcell                        # 只读
  name: T Cell Therapy
  title: High-purity T-cell expansion from leukopak to harvest
  desc: >
    Isolation and activation on the same bead, then expansion in serum-free medium.
  pill: CAR-T · TCR-T · TIL
  steps:                           # 固定 4 组，顺序即流程顺序
    - { label: Isolate,  text: CD3⁺ / CD4⁺ / CD8⁺ selection from PBMC or leukopak }
    - { label: Activate, text: CD3/CD28 beads or bead-free ActCel reagent }
    - { label: Expand,   text: IL-2 / IL-7 / IL-15 and IL-21 cocktails }
    - { label: Engineer, text: Viral or non-viral gene delivery support }
  products: [actsep-cd3-cd28, actcel-t-activation, maxsortin-cd3, il2, il7, il15]
```

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `id` | string | 是 | 只读，`^[a-z]+$` |
| `name` | string | 是 | ≤ 40 |
| `count` | — | — | **废弃**：改为构建期 `sum(1 for p in PRODUCTS if id in p.apps)` |
| `title` | string | 是 | ≤ 90 |
| `desc` | string | 是 | ≤ 300 |
| `pill` | string | 是 | ≤ 60，用 ` · ` 分隔 |
| `steps` | object[] | 是 | 恰好 4 组 `{label, text}` |
| `products` | string[] | 是 | 4–6 个 slug，必须存在于 `products.yaml` |

## 4. `faq.yaml`

```yaml
- question: Are your products available at GMP grade?
  answer: >
    Yes. The majority of the bead, antibody and cytokine portfolio is available in GMP grade
    manufactured under ISO 13485 and ISO 9001 quality systems.
```

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `question` | string | 是 | ≤ 120 |
| `answer` | string | 是 | ≤ 800，纯文本，允许内联 HTML 链接 |

## 5. `articles.yaml`

```yaml
- img: texture-network              # 只填文件名，输出 assets/img/brand/<img>.webp
  tag: Regulatory
  date: 12 Sep 2026                 # 原样显示的字符串，不是 ISO 日期
  title: What an FDA DMF actually buys you when you licence a CGT raw material
  excerpt: A Type II DMF is not an approval — it is a closed reference.
```

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `img` | string | 是 | 文件名（不含路径与扩展名），`assets/img/brand/<img>.webp` 必须存在 |
| `tag` | string | 是 | ≤ 24 |
| `date` | string | 是 | 展示用字符串，格式 `DD Mon YYYY`（如 `12 Sep 2026`） |
| `title` | string | 是 | ≤ 90 |
| `excerpt` | string | 是 | ≤ 200 |

## 6. `site.yaml`

```yaml
name: T&L Biotechnology
legal: T&L Biotechnology Ltd.
email: info@tlbiotechnology.com
phone: "+1 442 944 9891"
phone_raw: "4429449891"          # tel: 链接用，只读
us_address: 6076 Corte Del Cedro, Carlsbad, CA 92011, United States
hours: Mon–Fri, 9:00–17:00 (PT)
founded: 2011
dmf: ["038124", "038820"]
site_url: https://www.tlbiotechnology.com     # 只读，部署参数
og_image: assets/img/brand/og-cover.png
turnstile_sitekey: ""                        # 只读，改它需开发
```

| 字段 | 类型 | 必填 | 后台可改 |
|---|---|---|---|
| `name` / `legal` | string | 是 | 是 |
| `email` | email | 是 | 是（改它同时影响表单兜底 mailto） |
| `phone` / `phone_raw` | string | 是 | 部分（`phone_raw` 只读） |
| `us_address` | string | 是 | 是 |
| `hours` | string | 是 | 是 |
| `founded` | number | 是 | 是 |
| `dmf` | string[] | 否 | 是（需 QA 提供文号） |
| `site_url` | url | 是 | 否 |
| `og_image` | path | 是 | 是 |
| `turnstile_sitekey` | string | 否 | 否 |

## 7. `categories.yaml`（只读）

```yaml
- id: beads
  name: Cell Separation & Activation
  short: Beads
  blurb: Magnetic beads and bead-free activation reagents for T-cell workflows.
  icon: magnet                      # 复用内置图标集
  tag: Nanobeads and activation reagents
  img: actsep-cd3-cd28              # 分类卡片图名，输出 <img>-tile.webp
```

| 字段 | 类型 | 必填 | 约束 |
|---|---|---|---|
| `id` | string | 是 | 只读，`^[a-z]+$` |
| `name` | string | 是 | ≤ 40 |
| `short` | string | 是 | ≤ 16，用于卡片角标 |
| `blurb` | string | 是 | ≤ 160 |
| `icon` | string | 是 | 必须存在于 `build_site.py` 的 `ic()` 图标集 |
| `tag` | string | 是 | ≤ 60 |
| `img` | string | 是 | 产品 slug 或图片名，缺图 `check.py` FAIL |

> 结构稳定、一年改不到一次，后台只读。新增分类必须同时提供 `<img>-tile.webp`，
> 否则 `check.py` 会因缺图 FAIL。

## 8. 不纳入本期的内容

以下变量仍留在 `tools/content.py`，确认本期不做：

| 变量 | 用途 |
|---|---|
| `POSITIONING`、`STACK`、`LOOP` | 首页/平台页叙述 |
| `SERVICES` | 服务页卡片 |
| `PORTFOLIO_NOW` / `PORTFOLIO_NEXT` | 产品路线图 |
| `AUTOMATION`、`NETWORK`、`EXPERT` | 平台与产能页 |
| `NAV` | 导航结构（改它属于信息架构变更） |

## 9. 校验规则（实现清单）

按优先级排队，前三条在后台保存时拦截，其余在构建时拦截：

1. 必填与长度：见各字段表
2. 枚举合法性：`cat` ∈ categories，`apps` ⊆ applications
3. 引用完整性：`applications[].products` ⊆ products 的 slug；每项 ≥ 1
4. 唯一性：`slug` 唯一；`name` 唯一（重名会让搜索和 PDF 混乱）
5. 图片存在：`image_tile` / `image` / `articles[].img` 文件存在
6. 事实格式：`specs` 中出现 `EU/`、`EU/mL`、`%` 等数值时保留原单位字符串，不做单位换算
7. 禁用词：英文文案不得出现 `best`、`leading`、`world-class` 等最高级表达（现有 `check.py` 未覆盖，建议新增）
8. 数量一致：`applications[].count` 由产品列表计算，禁止手写

## 10. 迁移映射（`tools/content.py` → `content/*.yaml`）

| 现有结构 | 目标 |
|---|---|
| `PRODUCTS[i]` 的 8 个键 | `products.yaml` 同名键；新增 `image_tile` / `image` 两个字段 |
| `CATEGORIES[i]` | `categories.yaml`，键名不变 |
| `APPLICATIONS[i]["count"]` | 删除，改为计算值 |
| `APPLICATIONS[i]["steps"]` 元组 | 转为 `{label, text}` 对象，便于表单编辑 |
| `FAQ` 的二元组 | 转为 `{question, answer}` |
| `ARTICLES[i]` | `articles.yaml`，键名不变 |
| `COMPANY` | `site.yaml`，键名不变 |

迁移后必须满足：`build_site.py` + `build_docs.py` + `build_dist.py` + `check.py` 全绿，
且 `dist/` 与迁移前逐文件哈希一致（`docs/*.pdf` 允许因 PDF 元数据时间戳变化）。

## 11. 变更记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2026-11-03 | 确认版：6 个 YAML、字段表、校验规则、迁移映射；`applications[].count` 改为计算值，`specs` 改为 `{k, v}` 数组 |
