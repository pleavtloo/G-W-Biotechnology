# v13 · 内容外置（M0）

日期：2026-11-03
范围：`tools/content.py` → `content/*.yaml`，`content.py` 降为加载器。

## 为什么

市场部要自助改产品资料，CMS 无法直接写 Python 字典。先把数据挪到 YAML，
渲染器（`build_site.py` / `build_docs.py` / `build_dist.py`）**一行不改**。

## 结构变化（三处）

| 项 | 之前 | 之后 |
|---|---|---|
| 产品规格 | `specs={"Target": "..."}` 字典 | YAML 里是 `[{k, v}]` 有序数组，加载器转回字典 |
| 应用步骤 | `steps=[("Isolate", "...")]` 元组 | YAML 里是 `[{label, text}]`，加载器转回元组 |
| 应用产品数 | `count=14` 手写在 `APPLICATIONS` 里 | YAML 里没有该字段，加载器按 `PRODUCTS[].apps` 计算 |

前两项是纯形态转换，渲染结果不变；第三项**修正了错误数据**（见下）。

## 迁移前后的数字（手写 vs 实际）

| 应用 | 页面原来显示 | 实际产品数 |
|---|---|---|
| tcell | 14 | 18 |
| nk | 9 | 8 |
| msc | 7 | 5 |
| ipsc | 11 | 8 |
| hsc | 6 | 4 |
| dc | 8 | 7 |

容器：`mega menu`、首页 `apps__tab`、应用页 `appside__head`。合计从 55 变成 50。

## 验证方法

1. 迁移前记录 `dist/` 212 个文件的 SHA-256 基线。
2. 迁移后重建，比对：**只有 12 个 HTML 变化**，`data.js`、CSS、图片、90 份 PDF 全部字节一致。
3. 用迁移前的 `content.py` 重建一份，与迁移后逐行 diff：差异**全部**是上述计数，
   每页 5 行（mega 一行含 6 个数字），`index.html` 28 行（含 6 个 tab），`applications.html` 23 行（含 6 个侧栏）。
4. `python tools/check.py` → PASS（48 项硬检查）。

## 回滚

`content.py` 原文件在本目录留档。要整体回退 M0：

```powershell
Copy-Item versions/v13_content-yaml_20261103/content.py tools/content.py -Force
python tools/build_site.py
python tools/build_dist.py
```

`content/*.yaml` 可以保留，不影响旧加载器。

## 未做

- `SERVICES`、`NAV`、`POSITIONING`、`STACK`、`LOOP`、`PORTFOLIO_*`、`AUTOMATION`、`NETWORK`、`EXPERT`
  仍在 `content.py` 内联（`CONTENT-SCHEMA.md` 第 8 节）。
- 图片未迁到 CMS：`content/*.yaml` 里记录的是仓库内相对路径，构建时仍由 `build_site.py` 拼路径。
