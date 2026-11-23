# 明日继续（RESUME）

> 最后更新：2026-11-03 深夜。换机器或重开会话时，先读这份，再读 `CODEBUDDY.md`。

## 已完成

| 项目 | 状态 | 位置 |
|---|---|---|
| 表单接口加固（P03） | 完成 | `server/worker.js`、`server/dev_server.py`、`main.js` 表单段 |
| 产品助手（替代假 AI 客服） | 完成 | `main.js` 的 `answerFor()`、`build_site.py` 的 AI 面板 |
| 内容外置（M0） | 完成 | `content/*.yaml` + `tools/content.py` 加载器 |
| 后台页面（M1 部分） | 完成 | `website/admin/index.html`、`config.yml` |
| OAuth 桥 Worker | 已部署 | `server/oauth-worker/`，`https://tl-oauth.tlbiotechnology.workers.dev` |
| 后台登录 | **未打通** | 缺 GitHub OAuth App 的 client id / secret |

## 云端资源（已创建，勿重复建）

| 资源 | 标识 |
|---|---|
| Cloudflare 账号 | `a341e2bc5f5ad6d384b7acc1d87311cc`（Pleavtljy@gmail.com） |
| workers.dev 子域 | `tlbiotechnology` |
| Worker `tl-site-api` | `https://tl-site-api.tlbiotechnology.workers.dev`；变量 `ENVIRONMENT=staging`（部署时用 `--var` 覆盖，文件里仍是 production） |
| KV `LEAD_KV` | `cbb9fcd826e64670ad3e752e5ffca45a`，已写入 `server/wrangler.toml` |
| Worker `tl-oauth` | `https://tl-oauth.tlbiotechnology.workers.dev`；**secrets 未设置** |
| GitHub 仓库 | `git@github.com:pleavtloo/T-L-Biotechnology.git`，main 分支 |

## 明天的顺序

1. **创建 GitHub OAuth App**（只能网页操作）
   - https://github.com/settings/developers → New OAuth App
   - Homepage: `https://www.tlbiotechnology.com`
   - Callback: `https://tl-oauth.tlbiotechnology.workers.dev/callback`
   - 把 Client ID / Secret 存进 `%USERPROFILE%\.gh-oauth`（两行 `CLIENT_ID=…` / `SECRET=…`）
2. 写 worker secret 并验证：
   ```powershell
   cd server/oauth-worker
   wrangler secret put GITHUB_CLIENT_ID
   wrangler secret put GITHUB_CLIENT_SECRET
   ```
3. 真实走一遍 `/admin/` 登录，确认能看到 42 个产品
4. 部署静态站到 Cloudflare Pages（`dist/`），绑定 `/api/*` 路由
5. GitHub Actions：`build_site → build_docs → build_dist → check.py`，门禁失败不许发布
6. 收尾项：Turnstile sitekey/secret、Resend key、CRM webhook、SPF/DKIM/DMARC

## 环境坑（换机器必读）

| 现象 | 原因 / 处理 |
|---|---|
| `python` 不可用（9009） | 是 Store 占位符，用 `py`（3.12.10） |
| `git` / `node` / `wrangler` 不在 PATH | 分别加 `C:\Program Files\Git\cmd`、`C:\Program Files\nodejs`、`%APPDATA%\npm` |
| `github.com:443` 超时 / RST | 公司网络定向阻断。已配 `~/.ssh/config` 走 `ssh.github.com:443`，push 用 SSH 正常 |
| `*.workers.dev` 打不开 | DNS 污染（解析到 Meta/Dropbox 的 IP）+ SNI RST。浏览器预览需绑自有域名 |
| `cdn.jsdelivr.net` RST | admin 页面改用 `unpkg.com` |
| 构建输出乱码 | PowerShell `>` 是 UTF-16，读日志用 `-Encoding utf8` 或 `Out-File -Encoding utf8` |
| `build_docs.py` 只能在 Windows 跑 | `FONT_DIR = "C:/Windows/Fonts"` 写死，且仓库里没有字体文件。CI 因此跳过 PDF 重建（PDF 已提交在 `website/docs/`） |
| `github.com:443` 之外的 git 依赖 | git / node / wrangler 均不在默认 PATH，命令前需临时追加 |

## 本机上的东西（不备份会丢）

| 路径 | 内容 | 丢了怎么办 |
|---|---|---|
| `%USERPROFILE%\.ssh\id_ed25519*` | 推 GitHub 的私钥 | 重新 `ssh-keygen` 并在 GitHub 加公钥（1 分钟） |
| `%USERPROFILE%\.ssh\config` | github.com → ssh.github.com:443 | 重建，内容见下 |
| `%APPDATA%\xdg.config\.wrangler\config\default.toml` | Cloudflare 登录态 | `wrangler login` 重新授权 |
| `%USERPROFILE%\.gh-oauth` | OAuth App 凭据（待创建） | GitHub 后台重新生成 secret |

`~/.ssh/config` 内容：

```
Host github.com
  HostName ssh.github.com
  Port 443
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
```

## 不需要备份

`dist/`、`shots/`、`server/outbox/`、`tools/__pycache__/`、`.venv/`、`*.log` —— 全部可再生，已在 `.gitignore`。

`versions/` 与 `website/` 的图片、PDF 都在仓库里，不用单独存。

## 一条命令验证仓库健康

```powershell
py tools/build_site.py; py tools/build_dist.py; py tools/check.py
```

预期最后一行：`PASS - 48 hard checks clean`（外加一条 Turnstile sitekey 缺失的 warn，属已知）。

## 自动部署（2026-11-05 启用）

阿里云测试机 `47.93.183.103`：

```
/opt/tl-src        仓库克隆（deploy key 只读，不能推）
/opt/tl-src/deploy.sh   拉取 → build_site → build_dist → rsync 到 /var/www/tl
crontab            */2 * * * *  每 2 分钟检查一次提交
/var/log/tl-deploy.log   部署日志（含失败原因）
```

后台改内容 → GitHub 提交 → 2 分钟内自动上线，无需人工。

注意：`build_docs.py` 不在服务器跑（字体硬编码 Windows），90 份 PDF 仍由本地生成后提交。
