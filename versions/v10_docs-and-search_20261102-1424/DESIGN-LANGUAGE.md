# T&L Biotechnology 官网 · 设计语言

> 版本 v5 · 2026-10-26
> 适用：`website/` 下 13 个页面（11 个业务页 + 2 个设计评审页）
> 本文档描述"为什么这样设计"和"怎么照着做"，不是组件 API 手册。

---

## 0. 一句话定义

**一个用编辑式排版承载科学证据的企业站。**

不是产品画册，也不是 SaaS 落地页。它假设来访者**都很专业，但不是同一种专业**：科学家读参数，采购看交期，QA 核 DMF，经销商算价差。所以设计的第一任务是**分层披露**——概览层所有人都能读，细节层专业人能挖到；第二任务才是让证据自己站出来：数字要大、层级要清、颜色要克制。

---

## 1. 设计原则

| # | 原则 | 具体表现 | 反例（不做） |
|---|---|---|---|
| 1 | **证据优先于形容词** | 3,200 m²、DMF 038124、42 个 SKU 直接进首屏和信任条 | "行业领先""值得信赖" |
| 2 | **克制用色，一处一色** | 一屏只有一个强调色，深色区块承担节奏 | 彩虹标签、彩色渐变按钮 |
| 3 | **结构化，不装饰化** | 序号 01–06、四层栈、五步流程，让内容自己成体系 | 无意义的插画、装饰线条 |
| 4 | **密度可读** | 正文 16px / 1.6，卡片描述 13–14px，信息密但不挤 | 大留白配三行字 |
| 5 | **每一步都有下一个动作** | 每个区块底部都有链接或按钮，不出现"死胡同" | 只展示不引导 |
| 6 | **分层披露，不设身份门槛** | 概览 → 细节两级，谁都能读、专业人能挖 | 首页让访客先选"我是谁" |

---

## 2. 受众与浏览逻辑

### 2.0 四类来访者，四种判断标准

站点不服务单一受众。同一批页面要同时回答四种不同的问题，靠**分层信息披露**解决：概览层给所有人，细节层给专业人。

| 受众 | 他们真正在问 | 主入口 | 判断依据 | 期望的下一步 |
|---|---|---|---|---|
| **研发科学家** | 这个试剂能不能用在我的实验里 | Products · Applications | 规格、纯度、批间差、protocol | 下样品 / 问技术 |
| **采购与供应链** | 好不好买、多久到、多少钱 | Products（带起价）· Contact | 价格、MOQ、交期、库存 | 询价 |
| **质量与法规** | 能不能过审计、能不能签质量协议 | Quality | DMF、ISO、审计包、可追溯 | 申请授权书 / 约审计 |
| **经销商与分销** | 能不能赚钱、有没有区域保护 | Partners | 价差、授权范围、OEM、市场支持 | 申请合作 |
| **投资人 / 媒体** | 这家公司有没有未来 | Platform · Company | 定位、路线图、团队、设施 | 约沟通 |

**四条设计含义**（这些直接决定了页面长什么样）：

1. **价格必须公开起价**。采购不会为"contact us"停留；科学家也想先判断预算够不够。
2. **质量页必须结构化**。QA 是拿着清单逐条核对的，文号、状态、文件名要能一眼扫到，不能埋在段落里。
3. **经销商必须有独立入口**。它的内容（授权、价差、OEM）和产品页逻辑完全不同，塞进 Products 会两边都讲不清。
4. **首页不承担分流职责**。首页保持 v1 的产品叙事，分流交给导航、页脚和 AI 客服——这也避免了首页变成"请选择您的身份"的选择题。

> **反面案例**：把首页做成三个大按钮「我是研发 / 我是采购 / 我是经销商」。看起来贴心，实际是在让访客先做一道自己也不确定的题——很多人同时是两种身份。

### 2.1 导航模型

```
Platform · Products · Applications · Services · Quality · Company
                                  └─ Partners（经销商入口，收在 Company 下）
```

六个一级项，按"你是谁 → 你要什么 → 你怎么用 → 你怎么信 → 你是谁"排序：

- `Platform` — 我们凭什么做这些（差异化）
- `Products` — 具体卖什么（转化入口，用行业通用词）
- `Applications` — 按实验场景找（降低选择成本）
- `Services` — 买不到现成的时候怎么办（客单价最高）
- `Quality` — 凭什么信（尽调入口）
- `Company` — 公司本身，含 Partners、资源、招聘（融资 / 渠道 / 媒体）

> **命名规则**：目录叫 `Products`，不叫 `Tools`。行业买家按 Products 找货。`tools` 只出现在定位语里。
> **归属规则**：Partners 放 Company 而不是一级导航——它是**合作关系**，不是产品品类；七个一级项会让导航失去焦点。

### 2.2 页面层级

```
L1  首页 ──────────────── 建立认知，四条分流
     │
L2  Platform / Products / Applications / Services / Quality / Company / Partners
     │
L3  产品详情（?p=slug）· 应用详情（锚点）· 资源（COA / FAQ）
```

三层为限。任何内容都能在 **3 次点击内**到达。

### 2.3 五条典型路径

| 访客类型 | 路径 | 设计支撑 |
|---|---|---|
| **找货的采购** | 首页 → Products → 筛选 → 详情 → Quote | 目录三列网格 + 侧栏筛选 + 卡片直接带起价 |
| **评估的技术** | 首页 → Applications → 某细胞类型 → 推荐试剂组 → 详情 | 六个应用标签，每个给出四步工作流 |
| **尽调的 QA/RA** | 首页 → Quality → DMF 表 → 文档清单 → 联系 | 文号做成表格，不埋在段落里 |
| **谈渠道的经销商** | 首页 → Company → Partners → 合作模式 → 申请 | 三种合作模式并列 + 明确的准入条件 |
| **看公司的人** | 首页 → Company → 设施/里程碑 → 联系 | 数据面板 + 时间线 |

### 2.4 每页的"下一个动作"

| 页面 | 主 CTA | 次 CTA |
|---|---|---|
| 首页 | Explore the catalogue | Talk to a scientist |
| 平台 | Talk to an application scientist | See the services |
| 产品目录 | Quote（每卡） | Request a quote（底部） |
| 产品详情 | Request a quote | Datasheet |
| 应用 | Shop … reagents | Full workflow |
| 服务 | Scope a project | Automation roadmap |
| 质量 | Schedule an audit | Request a letter of authorisation |
| **合作** | **Apply to partner** | **Talk to channel team** |
| 公司 | Send an introduction | Quality overview |

---

## 3. 布局系统

### 3.1 栅格与容器

| 项 | 值 |
|---|---|
| 容器最大宽 | `1240px` |
| 页面左右留白 | `24px`（移动端 `18px`） |
| 主栅格 | 12 列思维，实现上用 `grid` 的 1/2/3/4 等分 |
| 常用分栏 | 首页 Hero `1.02fr / 0.98fr`；应用页 `1fr / 1fr`；产品页 `268px / 1fr` |
| 顶栏高度 | 38px（utility）+ 72px（nav） |

### 3.2 垂直节奏

```css
.section       { padding-block: clamp(56px, 7vw, 104px); }
.section--tight{ padding-block: clamp(40px, 4vw, 64px); }
.section-head  { margin-bottom: 44px; }
```

**规律**：区块之间 ≥ 56px，区块内部 ≤ 44px。留白永远大于内部间距，读者才能看出"这是两件事"。

### 3.3 四种区块底色

| 类型 | 用途 | 视觉 |
|---|---|---|
| **白** `--paper` | 默认，承载主要阅读 | — |
| **浅灰蓝** `--mist` `#F6F9FD` | 次级区块，做节奏切换 | 无边框 |
| **渐变蓝** `.section--tint` | 强调"流程/方法" | `#F4F8FE → #E9F1FB` + 上下 1px 描边 |
| **深海军蓝** `.section--ink` | 数据、质量、AI 能力 | `#07162A` + 分子纹理照片 + 0.88 黑蒙版 |

> **节奏规则**：连续两个区块不同色。深色区块每 3–4 个区块出现一次，作为视觉锚点，不超过整页 25%。

### 3.4 断点

| 断点 | 变化 |
|---|---|
| `> 1100px` | 完整布局 |
| `≤ 1100px` | 4 列 → 2 列；Hero 单列；侧栏取消 sticky |
| `≤ 860px` | 主导航收进抽屉；2 列 → 1 列；页脚 4 列 → 2 列 |
| `≤ 700px` | 表格横向滚动；AI 面板贴边 |
| `≤ 560px` | 全部单列；按钮撑满；AI 面板变底部抽屉 |

---

## 4. 色彩系统

### 4.1 品牌色（取自 logo）

| Token | 值 | 用途 |
|---|---|---|
| `--brand` | `#2A4299` | 主按钮、链接、强调数字、活跃态 |
| `--brand-deep` | `#1D3170` | 按钮 hover、深色区块基底 |
| `--accent` | `#2F8FD0` | 序号、次级强调、图标 |
| `--sky` | `#5FB7E8` | 深色区块上的强调、图形 |

### 4.2 中性色

| Token | 值 | 用途 |
|---|---|---|
| `--ink` | `#081729` | 标题、最重要的数字 |
| `--ink-soft` | `#1B2C44` | 正文 |
| `--muted` | `#5B6C86` | 次级正文、描述 |
| `--muted-2` | `#8394AB` | 元信息、单位、占位 |
| `--line` | `#E3EAF4` | 常规分隔线、卡片描边 |
| `--line-strong` | `#CCD8E9` | 输入框、可交互描边 |
| `--mist` / `--mist-2` | `#F6F9FD` / `#EEF3FA` | 区块底、标签底 |

### 4.3 语义色

| 语义 | 值 | 使用 |
|---|---|---|
| 成功 / 在线 | `#12876F`（文字）/ `#17A074`（点）/ `#ECFAF4`（底） | 在线状态、DMF "On file"、勾选 |
| 警示（仅文档） | `#C9A227` | 设计稿里的"注意"块，不进产品页 |

### 4.4 产品线分色（贯穿全站的身份编码）

| 产品线 | 色值 | 出现位置 |
|---|---|---|
| Cell Separation & Activation | `#2A4299` | 卡片顶条、序号胶囊、图标块、小标题 |
| Monoclonal Antibodies | `#1B7FA8` | 同上 |
| Recombinant Proteins | `#574CB0` | 同上 |
| Media & Culture Kits | `#2F8FD0` | 同上 |

> 实现方式：卡片上挂 `--cat` 变量，所有子元素用 `var(--cat)` 取色。加新产品线只需加一个 class。

### 4.5 深色区配色

背景 `#07162A` + 分子纹理图 + `rgba(6,19,36,.88)` 蒙版；
文字 `rgba(255,255,255,.72)`，标题纯白，强调 `--sky`。
卡片底 `rgba(255,255,255,.04)`，描边 `rgba(255,255,255,.14)`。

### 4.6 用色比例

**60 / 30 / 10**：60% 白与浅灰蓝，30% 深海军蓝区块，10% 品牌蓝强调。
品牌蓝只出现在：主按钮、链接、序号、活跃态、产品线编码。**不做大面积蓝色背景**（除深色区块）。

---

## 5. 字体与排版

### 5.1 字体

| 项 | 值 |
|---|---|
| 主字体 | **Inter**（可变字重 400–800，自托管 `inter-latin.woff2`，48KB） |
| 回退栈 | `-apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial` |
| 特性 | `font-feature-settings: "ss01", "cv05"`（单层 a、单层 g） |
| 数字 | `font-variant-numeric: tabular-nums`（所有价格、统计、序号） |

> 自托管原因：避免 Google Fonts 在国内不可达导致字重回退、版面跳动。

### 5.2 字阶

| 层级 | 字号 | 字重 | 字距 | 行高 |
|---|---|---|---|---|
| H1 / Hero | `clamp(2.5rem, 4.6vw, 4rem)` | 680 | `-0.035em` | 1.12 |
| H2 / 区块标题 | `clamp(1.85rem, 2.9vw, 2.65rem)` | 650 | `-0.03em` | 1.12 |
| H3 / 卡片标题 | `clamp(1.15rem, 1.5vw, 1.4rem)` | 650 | `-0.022em` | 1.12 |
| 正文 | `16px` | 400 | 0 | 1.6 |
| 导语 | `1rem–1.125rem` | 400 | 0 | 1.62 |
| 卡片描述 | `0.8–0.86rem` | 400 | 0 | 1.5 |
| 元信息 / 标签 | `0.66–0.78rem` | 550–650 | `0.05–0.14em` | 1.4 |
| Eyebrow（含序号） | `0.75rem` | 600 | `0.14em` | 1 |

### 5.3 排版规则

1. **大字负字距，小字正字距**。H1 用 `-0.035em` 收紧，全大写标签用 `+0.14em` 拉开。
2. **标题 `text-wrap: balance`**，避免孤字成行。
3. **正文最大宽度 62–66ch**，超过就换行——这是可读性的硬上限。
4. **单位与数字分离**：`3,200` 用大字，`m²` 用 `0.8rem` 的 `--accent` 色小字，视觉上不抢主数字。
5. **Eyebrow 结构**：`— 03 / NEW CAPABILITY`，短横线 + 序号 + 斜杠 + 标签，构成编辑式节奏。

---

## 6. 组件库

### 6.1 按钮

| 变体 | 用法 | 样式 |
|---|---|---|
| `.btn`（主） | 页面主行动 | 品牌蓝实心，高 48px，全圆角，hover 上浮 1px + 品牌阴影 |
| `.btn--ghost` | 次级行动 | 透明底 + `--line-strong` 描边，hover 变白底 + 深色描边 |
| `.btn--light` | 深色区上的主按钮 | 白底深字 |
| `.btn--outline-light` | 深色区上的次按钮 | 透明 + 白 28% 描边 |
| `.mini-btn` | 卡片内（COA / Quote） | 32px 高，7px 圆角 |

> 圆角：主按钮全圆（999px），卡片内小按钮 7px。**没有中间值**——要么胶囊，要么方块。

### 6.2 卡片

| 类型 | 用途 | 关键特征 |
|---|---|---|
| `.pcard` 产品族卡 | 首页四族 | 4:3 图 + 顶部 3px 产品线色条 + 右上序号胶囊 + 左下彩色图标 |
| `.fcard` 精选产品卡 | 首页精选 | 4:3 图 + 左上品类标签 + 名称（2 行截断）+ 起价 + 箭头 |
| `.gcard` 目录卡 | 产品目录 | 4:3 图 + 品类标签 + 名称 + 描述 + 价格/操作 |
| `.svc__card` 服务卡 | 服务 | 右上序号 + 渐变图标块 + 标签组，hover 顶部 2px 渐变线 |
| `.res__card` 资源卡 | 资源 | 16:9 暗色影像 + 标签胶囊 + 日期 + 标题 + 摘要 |
| `.qcard` / `.dcard` | 质量 / 说明 | 纯文本卡，44px 图标块 |

**卡片共同规则**：`1px var(--line)` 描边 + 16–20px 圆角 + hover 上浮 3–5px + 阴影加深。**不用彩色底**。

**文档下载（三种入口，同一份文件）**

| 入口 | 位置 | 形态 |
|---|---|---|
| 卡片角标 | `.gcard__dl` 产品卡图右下 | 32px 白底文件图标，hover 变品牌蓝 |
| 详情页 Documents 条 | 购买框下方 | `Datasheet PDF / COA PDF / SDS PDF` 三个文字链接 |
| 文档库 | `resources.html#docs` | 4 张共享文件卡 + 42 行表格（每行 3 个下载） |

> 判断：B2B 采购的决策顺序常常是"先看资料，再谈价格"。把文档放在询价按钮**之前**、卡片**之上**，等于承认这一点。所以卡片角标不是装饰，是第二入口。

### 6.3 标签与胶囊

- `.pill` — 中性信息（尺寸、数量），白底 + 描边
- `.pill--brand` — 强调（GMP、AI）
- `.pill--ok` — 状态（On file），浅绿底 + 圆点
- `.pcard__idx` / `.svc__idx` — 序号胶囊，产品线色文字
- `.toolrow__tag` — 路线图状态（In development / Research stage），灰色虚线感

### 6.4 表单

- 输入框高 46px（`.fld`）/ 48px（`.field-row`）/ 38px（AI 面板）
- 圆角 10px（表单）/ 全圆（订阅、AI 输入）
- 聚焦态：`border-color: var(--brand)` + `0 0 0 3px rgba(42,66,153,.1)`
- 深色区输入框需加 `.field-row--light`（白底、深字、深色 placeholder）——**这是踩过的坑**
- 提交后原地显示 `.form-ok` 绿色提示条，不做弹窗

### 6.5 表格

`table.data`：表头 `--mist` 底 + 全大写 0.7rem + 0.1em 字距；行高 15px 上下留白；hover 行 `#FCFDFF`；移动端 `min-width: 560px` + 横向滚动。

### 6.6 导航

**三层结构**：

1. **Utility bar**（38px，深色）— 一句资质声明 + 三个快捷链接
2. **Main nav**（72px，白，sticky，backdrop-blur）— logo + 六项 + 搜索 + Quote 按钮
3. **Mega menu**（860–980px 宽）— 左列分类、中列场景、右列深色推广卡

**Mega 定位**：JS 计算 `getBoundingClientRect()` 后夹取到视口内，防止首尾项溢出。**不要用纯 CSS `left:50%`**，在窄屏必然溢出。

**搜索入口（`.search-trigger`）**：不是图标按钮，而是**看起来像输入框的按钮**——236px 宽、浅蓝底 `#f4f8fe`、品牌蓝描边 `#c9d8ee`、放大镜 + 「Search 42 products」+ `⌘K` 提示。点击打开全站浮层。

| 断点 | 表现 |
|---|---|
| >1180px | 完整字段，显示 `⌘K` |
| 1000–1180px | 收窄到 168px，隐藏 `⌘K` |
| ≤1000px | 收成 40px 图标按钮 |
| ≤860px | 抽屉顶部出现 `.mm-search` 全宽搜索条 |

> 判断：搜索是这家站点**转化路径最短的入口**（买家多半带着型号或靶点来）。做成图标按钮等于把它藏起来；做成字段又不必真的放一个 input——按钮形态能省掉一次点击的心智成本，还能显示命中数量。

**移动端**：≤860px 收成独立 `.mobile-menu` 抽屉（`position:fixed`，z-index 85，低于 header 的 90），汉堡图标切换为 X。

> ⚠️ 坑：抽屉不能放在 `.header` 内部——`backdrop-filter` 会为 `position:fixed` 子元素创建包含块，导致定位错乱。

### 6.7 AI 组件（全站）

| 部件 | 规格 |
|---|---|
| 悬浮按钮 | 右下 24px，38px 头像 + 在线点 + "Ask T&L AI"，深色胶囊 |
| 面板 | 396px 宽，22px 圆角，深蓝渐变头部 |
| 数字人视图 | 172px 高，全幅影像 + 底部渐变 + 波形 + 字幕条 |
| 对话区 | 296px 高，`mask-image` 底部渐隐提示可滚动 |
| 输入区 | 38px 圆角输入 + 语音 + 发送 |
| 页脚 | `AI-generated · verify before use` + `Talk to a human scientist` |

**上下文规则**：在产品页打开时，问候语自动带入产品名（读 `?p=` → `window.TL.products`）。

**定位规则（重要）**：AI 的定位是**辅助完成实验**，不是"辅助搜索"。

- ✅ "Tell me what you need to express — the target, the yield, your timeline. I can propose a construct and a bench plan."
- ❌ "Ask me about a tool, a protocol or a document."（把 AI 降级成站内搜索）

所有 AI 文案必须指向**一个可执行的实验动作**（设计构建体、选宿主、排筛选矩阵），而不是指向"查询资料"。
快捷问题也按这个标准写：不是"IL-2 vs IL-7"，而是"Which host for a disulfide-rich domain?"。

平台层同理。四层不是"数据/模型/工具/实验室"，而是**一次实验的四段**：

| 层 | 在实验里的角色 |
|---|---|
| 01 Data | 上一轮实验留下的结果 |
| 02 Models | 设计这一轮做什么 |
| 03 Products | 这一轮消耗的材料 |
| 04 Lab network | 谁来执行这一轮 |

主标题也遵循同一规则：`AI plans the experiment. The bench runs it.`（不是 "AI narrows the search"——
"search" 暗示的是文献检索或序列空间搜索，会把平台拉回"工具/搜索"语境）。

---

## 7. 图像与图标

### 7.1 产品图处理

原始图是白底摄影，尺寸不一。统一流程：

1. 按内容包围盒裁成 **4:3**（保证瓶身完整、四周留 12% 余量）
2. 输出 `800×600` WebP，质量 88
3. 同时保留 `640×640` 方形版（用于头像、缩略图）
4. 卡片里 `object-fit: cover`，**不做透明抠图**——白底摄影本身就是资产，抠图反而破坏质感

### 7.2 背景纹理

| 资产 | 用途 |
|---|---|
| 60px 细网格 | Hero、页面头部，`rgba(42,66,153,.075)`，径向遮罩 |
| 模糊色块 | Hero 左上/右上，`filter: blur(90px)`，品牌蓝与天蓝 |
| 分子纹理照片 | `.section--ink` 背景，叠 0.88 黑蒙版 |

### 7.3 图标

- 线性图标，`stroke-width: 1.7`，24×24 viewBox
- 全部内联 SVG（无图标字体、无外链）
- 尺寸：卡片 17–22px，按钮 16–17px，标签 13px
- 色彩：继承 `currentColor`，hover 时随父级变色

### 7.4 数字人形象

`avatar-b1.jpg` — 半透明光体 + DNA 双螺旋。选择理由：小尺寸可辨识、生物技术语义内嵌、不像科幻反派。
使用尺寸：38px（悬浮按钮）/ 40px（面板头部）/ 26px（对话头像）/ 172px 高（数字人视图背景）。

---

## 8. 动效

### 8.1 时长与缓动

| 场景 | 时长 | 缓动 |
|---|---|---|
| 颜色 / 描边 | `0.18–0.2s` | ease |
| 按钮、卡片上浮 | `0.25–0.3s` | `cubic-bezier(.22,.61,.36,1)` |
| 面板展开 | `0.22s` | 同上 |
| 图片缩放 | `0.6–0.7s` | 同上 |
| 滚动揭示 | `0.7s` | 同上，交错 60ms |

> 统一缓动曲线：`cubic-bezier(0.22, 0.61, 0.36, 1)`——起步快、收尾缓，像有重量。

### 8.2 滚动揭示

`.reveal` 初始 `opacity:0; translateY(18px)`，`IntersectionObserver` 触发后归位。
同一组内元素按 `index % 6 × 60ms` 交错，避免整块同时弹出。

### 8.3 悬停层级

| 元素 | 变化 |
|---|---|
| 卡片 | 上浮 3–5px + 阴影加深 + 图片放大 1.05 |
| 按钮 | 上浮 1px + 品牌阴影 + 箭头右移 3px |
| 表格行 | 底色 `#FCFDFF` |
| 流程步骤 | 图标块填充品牌蓝 + "Explore" 链接淡入 |

**规则**：位移不超过 5px，缩放不超过 1.06。宁可小，不要晃。

### 8.4 减弱动效

`prefers-reduced-motion: reduce` 时：
- 关闭所有 transition / animation
- 数字滚动直接显示终值（**不是从 0 开始**）
- 滚动揭示元素直接可见

---

## 9. 交互体验

### 9.1 反馈原则

- **即时**：所有可点击元素都有 hover 态，指针变化
- **就地**：表单提交原地显示结果，不跳页、不弹窗
- **可逆**：筛选有 Reset，搜索有 ESC，抽屉有 X
- **不打断**：AI 面板不遮导航，关闭后按钮回到原位

### 9.2 深链与状态

| 能力 | 实现 |
|---|---|
| 产品详情 | `product.html?p=<slug>`，JS 读取渲染 |
| 分类筛选 | `products.html?cat=beads`，自动勾选对应复选框 |
| 应用锚点 | `applications.html#tcell`，JS 处理 sticky 偏移 |
| 设计稿状态 | `#open` / `#presence`（仅评审页） |

### 9.3 键盘

- `Tab` 全站可达，`:focus-visible` 统一 2px 品牌蓝描边
- `ESC` 关闭搜索浮层 / AI 面板 / mega menu / 移动抽屉
- `Ctrl/⌘ + K` 打开搜索
- 搜索框 `Enter` 直达第一条结果

### 9.4 搜索

全站浮层搜索（不是页内搜索框）：读 `window.TL.products`，匹配名称 + 描述 + 品类 + **规格值**（所以 `EU/mL`、`E. coli`、`4.5 µm` 都能命中）。

| 状态 | 内容 |
|---|---|
| 空 | 热门检索胶囊（CD3 / CD28 / IL-7 / NK kit / DMF / CAR-T）+ 四个产品族（带 SKU 数） |
| 有输入 | 命中数 + 最多 6 条结果（缩略图 / 名称 / 族 / 起价）+ 「See all N in the catalogue」 |
| 无命中 | 建议词 + 转人工入口，不留死胡同 |

**空状态必须给内容**。一个空白搜索框会让人以为"没东西可搜"；给出热门词和品类，等于替访客想起他要找什么。

**深链**：`products.html?q=CD3` 会把词填进目录搜索框并即时过滤——搜索结果页和浮层结果指向同一个状态，不做两套。

**键盘**：`⌘/Ctrl + K` 打开，`ESC` 关闭，`Enter` 进第一条结果。

---

## 10. 响应式策略

| 断点 | 核心变化 | 保留什么 |
|---|---|---|
| 1100px | 四列 → 两列，Hero 单列 | 全部内容 |
| 860px | 导航进抽屉，侧栏筛选折叠 | 全部内容 |
| 700px | 表格横向滚动 | 全部内容 |
| 560px | 全单列，按钮撑满，AI 变底部抽屉 | 全部内容 |

**原则**：不隐藏内容，只重排。唯一例外是装饰性的 Hero 浮层（色块、浮动卡）在小屏隐藏。

**移动端三个专门处理**：
1. 产品筛选折叠为「Filters」按钮 + 已选数量角标
2. 面包屑隐藏中间层级，末级省略号截断
3. AI 面板从右下角浮层变为底部全宽抽屉

---

## 11. 可访问性

| 项 | 现状 |
|---|---|
| 对比度 | 正文 `#1B2C44` on `#FFF` ≈ 13.9:1；`--muted` ≈ 5.3:1；满足 AA |
| 焦点 | 全局 `:focus-visible`，2px 品牌蓝 + 2px 偏移 |
| 语义 | `header / nav / main / section / article / footer`，`aria-expanded`、`aria-controls`、`aria-label` 齐全 |
| 图片 | 产品图有 `alt`，装饰性图片 `alt=""` |
| 动效 | 完整支持 `prefers-reduced-motion` |
| 键盘 | 无键盘陷阱；抽屉可用 ESC 关闭 |

**待补**：AI 面板尚未做焦点锁定（focus trap），打开后 Tab 仍可走到背后内容。

---

## 12. 文案规范

### 12.1 语气

**像一位做过实验的人，不像市场部。** 短句、具体、可验证。

| 场景 | 写 | 不写 |
|---|---|---|
| 标题 | "Raw materials that survive regulatory review." | "Industry-leading quality solutions" |
| 说明 | "50 nm nanobeads, untouched isolation, no bead removal." | "Advanced nanotechnology platform" |
| 承诺 | "Replies within one business day." | "Fast response" |
| 边界 | "We are not a CRO." | 回避 |

### 12.2 句式

- 标题优先**动词或名词短语**，不用问句（除 CTA）
- 一段不超过 3 句，一句不超过 25 词
- 数字写在前面：`3,200 m²`、`42 products`、`DMF 038124`
- 用具体名词替代形容词：`50 nm` 而不是 `ultra-small`

### 12.3 禁用

- ❌ 最高级形容词（best / leading / world-class）
- ❌ 未经验证的数字（客户数、市占率）
- ❌ 中文标点混入英文正文
- ❌ 品牌名简写不一致（统一 `T&L`，不写 `TL` / `T and L`）
- ❌ **自我披露能力缺口**（"We are not automated yet" / "manual today" / "lower throughput"）

**关于最后一条**：诚实不等于自曝短板。网站上写"我们目前是手工的、通量低"，
对客户是劝退、对投资人是减分，而这类信息在尽调时自然会披露。

正确做法是**描述提供什么，不描述缺什么**：

| ❌ 不要写 | ✅ 改成 |
|---|---|
| Today: expert-led, **manual** | Available now: **bench-scale, expert-led** |
| **lower throughput**, better judgement | small batches, tight iteration |
| We are not automated yet | （不写；用路线图的可用时间表达） |
| roadmap published, not implied | capacity roadmap with committed windows |

能力分层可以写时间（Available now / Rolling out 2026–27 / From 2027），
但每一档都要写**客户得到什么**，而不是**我们缺什么**。

### 12.4 术语表

| 用 | 不用 |
|---|---|
| Products | Tools（指目录时） |
| CGT / cell and gene therapy | gene therapy（范围太窄） |
| RUO / GMP grade | research grade（不规范） |
| application scientist | sales rep |
| capacity network | outsourcing / subcontracting |

---

## 13. 技术框架与实现

### 13.1 技术栈总览

**结论先说：没有前端框架，没有构建工具，没有 npm 依赖。**

| 层 | 选型 | 版本 / 规格 |
|---|---|---|
| 页面 | 静态 HTML5 | 11 个业务页，构建生成 |
| 样式 | **原生 CSS**，单一文件 | `style.css` 5,654 行，CSS 自定义属性驱动 |
| 脚本 | **原生 JavaScript**（ES5 语法，IIFE 封装） | `main.js` 489 行，零依赖 |
| 数据 | 构建期生成 `window.TL` JSON | `data.js`，42 个 SKU |
| 构建 | **Python 3.13** 脚本 | `build_site.py` 2,141 行 + `content.py` 567 行 |
| 字体 | 自托管 WOFF2 | Inter 可变字重，48 KB |
| 图片 | WebP | Pillow 生成，84 个产品图（2 种尺寸） |
| 部署 | 任意静态托管 | 无需 Node、无需运行时 |
| 版本 | 目录快照 | `versions/v1…v5`，含 VERSION.md |

### 13.2 为什么不用框架

| 考虑 | 判断 |
|---|---|
| 页面数量 | 11 个业务页、内容为主，React/Vue 的组件复用收益低于其运行时成本 |
| 首屏性能 | 无框架 → 首页 HTML 79 KB + CSS + 字体，首屏 JS 执行 < 10 ms |
| 交付对象 | 客户 IT 可能只会 FTP 上传；纯静态文件丢到任何服务器都能跑 |
| 长期维护 | 三年后不会因为框架大版本升级而重写 |
| 内容更新 | 改 `content.py` 跑一次脚本，比教运营用 CMS 更实际 |

> **代价**：组件复用靠 Python 函数而非组件库；状态管理靠 DOM class 而非数据流；没有 HMR，改样式要手动刷新。这些代价在 11 个业务页的规模下可接受，超过 30 页就应该换框架。

### 13.3 构建流程

```
content.py  ──┐
              ├──> build_site.py ──> website/*.html + data.js
（纯数据）     │      （模板函数）
              │
              └──> 每个 page_*() 返回完整 HTML 字符串
```

- 每个页面对应一个 `page_xxx()` 函数，内部用 Python f-string / `.format()` 拼装
- 共享外壳 `head() / header() / footer()` 保证全部页面的导航与页脚完全一致
- 产品数据只维护在 `content.py` 的 `PRODUCTS` 列表，`data.js` 由构建自动生成
- 数量类文案统一用 `NSKU = len(PRODUCTS)` 计算，避免"41 vs 42"这类不一致

```bash
python tools/build_site.py      # 重建全部页面
python tools/build_docs.py      # 重建 90 个 PDF 文档
```

**文档流水线**（`build_docs.py`，fpdf2）：

```
content.py ──> build_docs.py ──> website/docs/*.pdf
                                  ├─ datasheet-<slug>.pdf  ×42（2 页）
                                  ├─ coa-<slug>.pdf        ×42（1 页）
                                  ├─ sds-<cat>.pdf         ×4（16 节）
                                  └─ dmf-summary / quality-overview
```

- 版式用同一套品牌色与字阶（Calibri 自 Windows 字体目录加载，覆盖 µ / ≤ / ⁺ / ® 等字符）
- 订单号 `TL-<族码>-<序号>`、批次号由 slug 哈希生成——**同一 SKU 每次生成结果一致**，不会因为重建而漂移
- 产品改完必须重跑，否则页面链接指向的 PDF 还是旧内容

> 坑：fpdf2 的 `multi_cell` 默认 `new_x=RIGHT`，标题后紧跟副标题会从标题末尾继续写，直接冲出右边界。所有标题调用都要显式 `new_x="LMARGIN", new_y="NEXT"`。

### 13.4 浏览器特性依赖

站点用了若干现代 CSS 特性，**需要常青浏览器**（Chrome / Edge 111+，Safari 16.2+，Firefox 113+）：

| 特性 | 用途 | 降级表现 |
|---|---|---|
| `color-mix()` | 卡片 hover 描边混色（4 处） | 描边保持原色，无视觉损失 |
| `mask-image` | Hero 网格渐隐、对话区底部渐隐 | 无渐隐，内容仍完整 |
| `aspect-ratio` | 所有图片容器 | 图片按原始比例，卡片高度可能不齐 |
| `clamp()` | 全部字号与间距 | 需手动写媒体查询 |
| `backdrop-filter` | 顶栏毛玻璃、浮层 | 变纯色底，可读性不受影响 |
| `:focus-visible` | 键盘焦点环 | 无焦点环（可访问性下降） |
| `IntersectionObserver` | 滚动揭示、数字滚动 | 元素直接可见（已做 fallback） |

> **明确不支持 IE11**。生命科学客户以 Chrome / Edge 为主，IE 占比可忽略。

### 13.5 性能预算

| 指标 | 当前值 | 预算 |
|---|---|---|
| 首页 HTML | 79 KB | < 120 KB |
| CSS（未压缩） | 约 180 KB | < 250 KB |
| JS（未压缩） | 约 18 KB | < 40 KB |
| 字体 | 48 KB（单文件，子集化） | < 80 KB |
| 首页首屏图片 | 5 张 WebP，约 180 KB | < 300 KB |
| 整站体积 | 3.5 MB | < 5 MB |

**没有做**：CSS/JS 压缩、图片懒加载之外的预加载、CDN、Service Worker。上生产前建议至少加 gzip/brotli（可省 70%）。

### 13.6 文件结构

```
website/
├── index.html … partners.html       11 个业务页
├── design-ai-entry.html             设计评审（上线前删）
├── design-avatar.html               设计评审（上线前删）
├── assets/css/style.css             唯一样式表（5,654 行）
├── assets/js/main.js                交互（489 行）
├── assets/js/data.js                产品数据（构建生成，勿手改）
├── assets/img/products/             42 个 SKU × 2 种尺寸 = 84 文件
├── assets/img/brand/                logo、纹理
├── assets/img/avatar/               数字人 4 版
└── assets/fonts/inter-latin.woff2
```

### 13.7 命名约定

| 类型 | 规则 | 例 |
|---|---|---|
| CSS 类 | BEM-lite，块 + 元素 | `.pcard` / `.pcard__media` / `.pcard--beads` |
| 修饰符 | `--` 双横线 | `.section--mist`、`.btn--ghost` |
| 状态 | `is-` 前缀 | `.is-open`、`.is-active`、`.is-in` |
| 变量 | 语义命名 | `--ink` 而非 `--dark-blue` |
| 产品 slug | 全小写连字符 | `actsep-cd3-cd28` |
| 页面函数 | `page_<name>()` | `page_partners()` |

### 13.8 加一个新页面

1. `content.py` 加数据（如需）
2. `build_site.py` 写 `page_xxx()`，复用 `head() / header() / footer()`
3. 注册到 `pages` 字典
4. 在 `NAV` 或页脚加链接
5. 跑构建，截图核对 1440px 与 390px

### 13.9 加一条产品线

1. `content.py` 的 `CATEGORIES` 加一项（`id`、`icon`、`tag`、`img`）
2. `style.css` 加 `.pcard--<id> { --cat: <color> }` 和 `.fcard--<id>`
3. 产品数据里 `cat` 指向新 `id`

---

## 14. 已知限制

| 项 | 说明 |
|---|---|
| AI 后端 | 未接，输入框提交只返回占位回复 |
| 数字人 | 静态图，不会说话；真口型驱动需 3D 绑定 + TTS |
| 规格参数 | 占位模板，需按真实 COA 核对 |
| 部分产品图 | CD4 / CD14 磁珠、CD20 抗体为同系列替代图 |
| 表单 | 前端演示，未接 CRM 或邮件服务 |
| 法务链接 | Privacy / Terms 为占位 |
| 焦点管理 | AI 面板无 focus trap |
| 国际化 | 仅英文；如需中英双语，建议用 `data-lang` + 文案表，而非复制页面 |

---

*本文档随站点演进更新。修改设计语言时，请同步 `style.css` 的 `:root` 与本文件。*
