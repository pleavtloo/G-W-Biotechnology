# T&L Biotechnology — 官网重设计

静态站点，9 个页面，2.3 MB，无构建依赖，可直接托管到任意静态服务器。

## 页面

| 文件 | 内容 |
|---|---|
| `index.html` | 首页：Hero / 信任条 / 五步工艺流 / 四大产品平台 / 应用分标签 / 数据与 DMF / 定制服务 / 资源 / CTA |
| `products.html` | 产品目录：41 个 SKU，按产品族 + 应用筛选，搜索、排序 |
| `product.html` | 产品详情：`?p=<slug>` 动态渲染，规格、文档、相关产品 |
| `applications.html` | 6 个应用场景，交替版式 + 推荐试剂组 |
| `quality.html` | 质量体系、DMF 表、文件清单、可追溯性 |
| `services.html` | 6 项定制服务 + 五阶段流程 |
| `resources.html` | COA 查询、技术文库、FAQ |
| `about.html` | 公司、平台、里程碑、荣誉、招聘 |
| `contact.html` | 询价表单、办公室、响应时效 |

## 设计说明

- **品牌色**取自 logo：`#2A4299` / `#3289CA` / `#5FB7E8`
- **字体** Inter（自托管 `assets/fonts/inter-latin.woff2`，无外链）
- **信息架构**双轴：按工艺流程（Isolate → Activate → Expand → Engineer → Release）+ 按细胞类型，对标 ACRO Biosystems / Sino Biological / Miltenyi 的页面逻辑
- **信任主线**贯穿全站：FDA DMF 038124 & 038820、ISO 13485 / 9001、3,200 m²、30+ 审计、Phase I 供货
- **响应式**断点 1100 / 860 / 560；移动端筛选折叠为按钮、抽屉式菜单、面包屑截断

### 视觉层次（第二轮加密度）
- Hero：双层模糊色块 + 60px 细网格 + 产品卡片浮层 + 副卡（第二个 SKU），不再是纯白
- 章节标题带序号（01 / 02 / 03…），建立编辑式节奏
- 工艺流程区改为浅蓝色带 + 每步图标卡
- 四条产品线各有独立色（#2A4299 / #1B7FA8 / #574CB0 / #2F8FD0），贯穿顶条、编号、图标、小标题
- 质量区背景换成分子纹理照片 + 深色蒙版；资源卡用真实科研影像
- 服务卡加编号与彩色图标，hover 有位移与描边变化

## 交互

- Mega menu（JS 计算定位，避免溢出视口）
- 搜索浮层：`Ctrl/⌘ + K`，实时匹配产品名与靶点
- 产品筛选 / 排序 / 空态；`products.html?cat=beads` 可深链
- 产品详情按 `?p=` 渲染；规格、文档、相关产品三个 tab
- 数字滚动、滚动淡入、FAQ 手风琴、表单提交提示
- 已处理 `prefers-reduced-motion`

## 内容来源与待核对项

事实均来自 tlbiotechnology.com（About / COA / 产品页）。**上线前需人工核对：**

1. **规格参数为占位模板**（纯度、内毒素、保存条件等），须按实际 COA / 说明书替换。
2. **产品图**取自原站缓存图，部分为同系列替代图（CD4 / CD14 磁珠、CD20 抗体）；建议换成官方产品摄影。
3. **DMF 表**只列了确认过的两个文号；CD3 抗体、IL-7、IL-15 的 DMF 号以"按要求提供"表述。
4. **年限**统一为 15 年（2011 年成立，2026 年），原站文案为"12+"，请确认口径。
5. 询价 / COA / 表单目前是前端演示，未接后端，需对接 CRM 或邮件服务。
6. 页脚"Privacy policy""Terms of sale"为占位链接。

## 修改方式

内容在 `../tools/content.py`（产品、应用、服务、FAQ、文章），
结构在 `../tools/build_site.py`（模板与页面组装）。

```bash
# 改完内容后重新生成全部页面
python ../tools/build_site.py
```

`assets/js/data.js` 由构建脚本自动生成，不要手改。
