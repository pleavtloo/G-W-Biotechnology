# P05 · 文档与 COA：从静态 PDF 到可查询的批次索引

**目标**：COA 从"每 SKU 一份代表性文件"变成"按批次号查得到、签发可追溯"。

**前置**：P03（表单与 KV 可用）。

**先读**：`CODEBUDDY.md`、`tools/build_docs.py`、`server/worker.js` 的 `handleCoa`、
`website/assets/js/main.js` 的 COA 表单段

---

## 现状与差距

| 现状 | 问题 |
|---|---|
| `docs/coa-<slug>.pdf` 每 SKU 一份 | 批次是虚构的，不能当正式文件 |
| `/api/coa` 用 KV 索引 | KV 里没有数据，永远返回 `found:false` |
| 无上传流程 | QA 签发后没有地方放 |

---

## 任务

### 1. 文件命名与存储

```
coa/<sku>/<lot>.pdf          例：coa/TL-BD-101/L43F8-538.pdf
coa/<sku>/<lot>.superseded.pdf   （旧版，保留但标记）
```

- 存储：R2（`COA_BUCKET`），公开读走签名 URL 或 Worker 代理
- 索引：KV `COA_INDEX`，key = `<lot>`，value：
  ```json
  {"file":"coa/TL-BD-101/L43F8-538.pdf","sku":"TL-BD-101","released":"2026-08-14","rev":"1"}
  ```

### 2. 查询接口改造

`POST /api/coa` 行为矩阵：

| 情况 | 响应 | 前端文案 |
|---|---|---|
| 命中 | `{found:true, url, sku, released}` | 直接下载 |
| 批次存在但未签发 | `{found:false, state:"pending"}` | 「该批次尚未放行，QA 会在 1 个工作日内联系你」 |
| 批次不存在 | `{found:false, state:"unknown"}` | 「未找到该批次，请核对标签或联系 QA」 |
| 格式非法 | `400` | 「批次号格式不正确，示例：TL603-2409A」 |

**不要**把三种"没查到"混成一句话——QA 每天要处理这些，混在一起会浪费大量沟通。

### 3. 上传工具（内部用）

`tools/coa_upload.py`（不部署，本地跑）：

```bash
python tools/coa_upload.py --sku TL-BD-101 --lot L43F8-538 --file ./scan.pdf --released 2026-08-14
```

- 校验：PDF 可打开、文件名规范、批次号未被占用（占用则提示 `--rev 2` 走替换）
- 上传 R2 + 写 KV 索引，两步都成功才算完成
- 打印一条可复制的确认信息给 QA

### 4. 页面改造

- `resources.html#coa` 表单：加格式提示与示例、加"三种结果"的对应文案
- 产品详情页 Documentation 标签：COA 那条改为「按批次查询」链接到 `resources.html#coa`
- `docs/coa-<slug>.pdf` 保留但改名为 `coa-sample-<slug>.pdf`，标签写 **Sample only**
  ——上线前这两个字必须存在，否则等于暗示那是真证书

### 5. 审计日志

每次查询记 `{evt:"coa", lot_hash, state, ip_hash, ts}`，保留 12 个月。
批次号是商业信息，日志里存哈希。

## 约束

- 不改 PDF 版式（`build_docs.py` 不动）
- 不把未签发批次的文件放进公开目录
- 不提供"批量下载全部 COA"——那等于泄露客户批次结构

## 验收

```bash
python tools/coa_upload.py --sku TL-BD-101 --lot TEST-0001 --file dist/docs/coa-actsep-cd3-cd28.pdf --released 2026-08-14
python server/dev_server.py 8080
# 查 TEST-0001 -> found:true + 可下载
# 查 TEST-9999 -> found:false, state:unknown
# 查 "abc"    -> 400
```

## 交付

- `tools/coa_upload.py`
- `server/worker.js` 的 `handleCoa` 四态实现
- `resources.html` 与产品页的文案与链接调整
- `docs/coa-sample-*.pdf` 改名 + Sample only 标签
- `server/README.md` 补充 R2 与 KV 的绑定说明

## 备注

上线前必须由 QA 提供**至少 3 个真实批次**跑通全流程。只有演示数据等于没做。
