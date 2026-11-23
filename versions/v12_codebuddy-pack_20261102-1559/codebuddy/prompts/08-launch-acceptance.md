# P08 · 上线验收：可量化的 go / no-go

**目标**：用一份能签字的标准决定"能不能上线"，而不是靠感觉。

**前置**：P00–P07 全部完成。

**先读**：`BUILD-PLAN.md` 第 8 节（验收标准）、`CODEBUDDY.md`

---

## 任务

### 1. 自动化验收

```bash
python tools/build_dist.py
python tools/check.py
python tools/eval_chat.py          # P04 后
python tools/lighthouse.py         # 见任务 2
```

全部通过才继续。

### 2. 性能与可访问性

写 `tools/lighthouse.py`：对 5 个关键页（首页、products、product、resources、contact）
跑 Lighthouse（Chrome 内置 CLI），输出 JSON 到 `reports/lighthouse/`。

门槛：

| 指标 | 移动端 | 桌面 |
|---|---|---|
| Performance | ≥ 85 | ≥ 95 |
| Accessibility | ≥ 95 | ≥ 95 |
| Best Practices | ≥ 95 | ≥ 95 |
| SEO | ≥ 95 | ≥ 95 |
| LCP | < 2.5s | < 1.5s |
| CLS | < 0.1 | < 0.1 |

不达标就修，不要改门槛。

### 3. 功能验收（逐条手测，记录结果）

| # | 场景 | 期望 |
|---|---|---|
| 1 | 首页 → 搜索 "CD3" → 进产品页 | 结果准确，价格显示 |
| 2 | 产品页下载 Datasheet / COA / SDS | 三个 PDF 都能打开 |
| 3 | resources 文档库任意一行三个下载 | 都可用 |
| 4 | 联系表单提交 | 收到回执邮件，CRM 有记录 |
| 5 | 表单断网提交 | 显示失败 + mailto 可点 |
| 6 | COA 查询（真批次 / 假批次 / 非法格式） | 三种不同文案 |
| 7 | AI 问 IL-7 内毒素 | 数值与 datasheet 一致，带引用 |
| 8 | AI 问"我该用哪个" | 明确转人工 |
| 9 | 移动端菜单 + 搜索 | 可用，无横向滚动 |
| 10 | 键盘走一遍首页 | 焦点可见，顺序合理 |
| 11 | 打印产品页 | 规格表完整 |
| 12 | 访问不存在 URL | 404 页，四个链接可用 |

### 4. 跨浏览器

Chrome / Edge / Safari / Firefox 最新两版，iOS 15+ Safari，Android 10+ Chrome。
每个至少走场景 1、4、9。

### 5. 合规检查

- [ ] Cookie 同意在分析脚本之前触发
- [ ] 隐私政策包含：收集什么、为什么、保留多久、如何删除
- [ ] AI 使用说明：能做什么、不能做什么、数据如何留存
- [ ] 页脚主体信息（公司名、地址、注册号）
- [ ] 所有 PDF 上的 "Representative / Sample" 标注与实际一致

### 6. 上线动作

1. 打 tag `v1.0.0`
2. 部署生产，跑一次冒烟（场景 1/4/6/12）
3. 提交 sitemap 到 Google Search Console + Bing
4. 打开监控三件套
5. 记录上线时刻与版本号到 `reports/launch.md`

## 约束

- 不改门槛迁就现状。不达标就修，或明确记录「已知缺陷 + 修复计划 + 负责人」。
- 不在验收阶段开新的视觉需求。
- 不跳过手测：自动化查不出「看起来不对」。
- 上线前必须删掉设计评审页与演示件，这一条不可协商。

## 验收

```bash
python tools/check.py && python tools/eval_chat.py
ls reports/lighthouse/*.json | wc -l     # 期望 5
```

`reports/launch.md` 里 12 条功能场景全部有"通过 + 时间 + 执行人"。

## 交付

- `tools/lighthouse.py` + 5 份 JSON 报告
- `reports/acceptance.md`（12 条场景结果）
- `reports/compliance.md`（5 条勾选）
- `reports/launch.md`（版本、时刻、冒烟结果、回滚方式）

## 备注

**唯一可以推迟上线的理由**是内容不齐或合规未过，不是"页面还能再好看一点"。
设计已经定稿，验收阶段不要开新的视觉需求——那会把上线拖成无限期。
