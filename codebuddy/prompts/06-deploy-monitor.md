# P06 · 部署与监控：Cloudflare Pages + Worker

**目标**：一条命令部署，出问题 5 分钟内知道。

**前置**：P03（API 可用）。P04/P05 可后补。

**先读**：`CODEBUDDY.md`、`tools/build_dist.py`、`server/wrangler.toml`、`server/README.md`

---

## 任务

### 1. Pages 项目

- 项目名 `tl-site`，构建命令 `python tools/build_dist.py`，输出目录 `dist`
- 环境变量：`PYTHON_VERSION=3.13`
- 预览分支：每个 PR 自动生成 preview URL
- 自定义域：`www.tlbiotechnology.com` 为主域，裸域 301 到 www

### 2. Worker 路由

- Worker `tl-site-api`，路由 `/api/*` 绑到 Pages 域
- 绑定：KV `COA_INDEX`、R2 `COA_BUCKET`（P05 用）
- Secrets：`RESEND_API_KEY`、`LEAD_TO`、`TURNSTILE_SECRET`、`CHAT_API_URL`、`CHAT_API_KEY`

### 3. CI（GitHub Actions）

`.github/workflows/deploy.yml`：

```yaml
on:
  pull_request:
  push:
    branches: [main]
jobs:
  build:
    steps:
      - checkout
      - setup python 3.13
      - pip install fpdf2 pyyaml pymupdf
      - run: python tools/build_site.py
      - run: python tools/build_docs.py
      - run: python tools/build_dist.py
      - run: python tools/check.py          # 失败即阻断合并
      - run: python tools/eval_chat.py      # P04 之后加，通过率 <85% 阻断
```

**`check.py` 必须阻断合并**。这是唯一能防止"看起来没问题"的门。

### 4. 监控（三件，缺一不可）

| 类型 | 工具 | 告警条件 |
|---|---|---|
| 可用性 | UptimeRobot | 首页 5 分钟探活，连续 2 次失败告警 |
| 表单 | Worker 日志 + 自建计数 | 1 小时内 0 条 lead → 告警（说明表单挂了） |
| 前端错误 | Sentry | 新错误类型首次出现即告警 |

第三条最容易漏。表单"没消息"和表单"没挂"看起来一样，**必须有反向探针**：
每天 9:00 用固定测试邮箱提交一次，成功则无动作，失败告警。

### 5. 回滚

- Pages 保留最近 10 次部署，一键回滚
- Worker 用 `wrangler rollback`
- 把回滚步骤写进 `server/README.md`，**并实际演练一次**，记录耗时

### 6. 备份

- `content/` 每日快照到 R2（`backup/content/<date>.tar.gz`），保留 30 天
- COA 文件本身就是主数据，开 R2 版本控制

## 约束

- 不引入 Vercel/Netlify 双托管，只用一套
- 不在仓库里存任何密钥，全部走 GitHub Secrets / wrangler secret
- 不关闭 `check.py` 的阻断

## 验收

```bash
# 1) 本地构建通过
python tools/build_dist.py && python tools/check.py

# 2) PR 触发 preview，访问 preview URL 检查首页与 404

# 3) 生产域访问，检查：
curl -sI https://www.tlbiotechnology.com | grep -E "strict-transport|content-type"
curl -s https://www.tlbiotechnology.com/api/health
curl -s https://www.tlbiotechnology.com/sitemap.xml | head -3

# 4) 故意推一个坏 commit（缺 meta description），确认 CI 阻断
```

## 交付

- `.github/workflows/deploy.yml`
- `server/wrangler.toml` 完整绑定
- `server/README.md` 增加：部署、回滚、告警配置三节
- 一次真实部署的截图（preview + 生产）
- 回滚演练记录（耗时、步骤）

## 备注

域名解析与发信域是客户侧操作。列一份**逐条可勾选**的清单给他们的 IT：
DNS A/CNAME、SPF、DKIM（两个 CNAME）、DMARC（`p=none` 起步）、DMARC 报告邮箱。
少一条，询价邮件就可能进垃圾箱。
