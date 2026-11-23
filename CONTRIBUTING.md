# 版本管理规范

这个仓库有一个特殊之处：**推送到 `main` 就等于上线**。

```
git push  →  GitHub  →  服务器 cron（每 2 分钟）  →  构建  →  线上
```

所以每次提交的重量比普通项目高。下面的规则都是围绕这一点设计的。

---

## 一、提交

### 格式

```
区域: 做了什么
```

区域用固定的几个前缀，方便以后 `git log --grep` 检索：

| 前缀 | 范围 |
|---|---|
| `Admin` | `/manage.html` 后台界面与接口 |
| `Checkout` | 结账页、付款方式、下单逻辑 |
| `Cart` | 购物车 |
| `Products` | 产品列表页、详情页 |
| `Account` | 注册、登录、改密码、找回密码、我的订单 |
| `Orders` | 订单存储、订单面板、发票 |
| `Legal` | Privacy / Terms / Shipping |
| `Deploy` | `deploy.sh`、cron、构建脚本 |
| `Data` | `content/` 下的内容变更 |
| `Docs` | 文档、README |

例：

```
✅ Checkout: require a signed-in, approved account before ordering
✅ Orders: respond before SMTP so checkout does not hang for 20 seconds
✅ Legal: JAMS arbitration in San Diego, restocking fee 15%
❌ update
❌ fix bug
```

### 粒度

**一个提交做一件事。** 如果提交信息里出现了「和」，多半该拆成两个。

反例：

```
❌ 改了结账页文案，同时修了部署脚本的锁
```

### 提交前

```bash
git status        # 确认没有意外的未跟踪文件
py tools/check.py # 门禁：48 项 + 唯一性 + 图片存在
```

`check.py` 不过就不要提交——服务器构建也会失败，而且线上会保持旧版本 2 分钟以上。

---

## 二、分支

单人开发不需要复杂流程，但有一条线：

| 改动 | 做法 |
|---|---|
| 改文案、修样式、加一个字段 | 直接推 `main` |
| 重构、换架构、动数据结构 | **开分支** |

判断标准：**出问题能不能 5 分钟内修好**。能，就直接推；不能，就开分支。

```bash
git checkout -b feature/checkout-v2
# ... 改 ...
git push -u origin feature/checkout-v2
# GitHub 上开 PR，自己看一遍 diff 再合并
```

### 多人协作时

`main` 需要开分支保护：

```
Settings → Branches → Add rule → Branch name: main
☑ Require a pull request before merging
☑ Require approvals: 1
```

否则任何人 push 都会直接上线，且没有二次确认。

---

## 三、标签

tag = 一个能可靠回到的状态。

```bash
git tag -a v2026.11.17 -m "完整购物流程上线"
git push origin v2026.11.17
```

该打的时候：

- 一个大功能做完并验证通过
- **域名切换前后各打一个**
- 准备大改之前（作为回滚点）
- 每月一次

命名用日期：`vYYYY.MM.DD`。比 `v1.2.3` 更适合这个项目——它没有语义化版本的需求，只需要知道「哪天是好的」。

---

## 四、回滚

线上出问题时，**先恢复，再排查**。

### 方式 A：撤销某次提交（推荐）

```bash
git log --oneline -5          # 找到出问题的提交
git revert <hash>             # 生成一个反向提交
git push                      # 2 分钟后线上恢复
```

历史完整，别人能看懂发生了什么。

### 方式 B：整体退回某个 tag

```bash
git reset --hard v2026.11.17
git push --force-with-lease
```

**会丢掉中间的提交。** 只在确认没有要保留的东西时用。

`--force-with-lease` 比 `--force` 安全一点：如果远端在你上次 fetch 之后有别人的新提交，它会拒绝。

### 回滚之后

1. 在本地重新做那个改动，这次小心
2. 下次打 tag 之后再继续

---

## 五、内容与代码的分工

这是这个项目最容易出问题的地方。

```
代码（tools/ server/ website/）  →  git 管，改完 push
内容（content/*.yaml）           →  服务器管，后台改
```

**内容不要从本地改**。原因：`deploy.sh` 部署时会用服务器上的 `content/` 覆盖，本地改的会被丢掉。

| 想改什么 | 正确做法 |
|---|---|
| 产品价格、规格、描述 | `/manage.html` → Products |
| FAQ、文章、应用页 | `/manage.html` |
| 银行账户、联系方式 | `/manage.html` → Site settings |
| 页面结构、样式、逻辑 | 改代码 → push |

### 内容同步回 git

GitHub 上的 `content/` 可能落后于线上（因为后台改的直接写服务器）。

目前靠手动同步：

```bash
# 从服务器拉最新内容，提交到 git
tar czf - -C /opt/tl-src content | ...
```

**每天同步一次**是最低要求，否则一旦服务器故障，git 里的内容历史会断档。

---

## 六、备份

三份副本，三个位置：

| 位置 | 内容 | 频率 |
|---|---|---|
| GitHub | 代码 + 内容 | 每次提交 |
| 服务器 `/opt/backups/` | 内容 + 订单 + 账号 | 每天 03:00，保留 14 天 |
| `contact@seafrom.com` 邮箱 | 同上 | 每周一 |

### 验证备份可用（每季度做一次）

备份没验证过等于没有。检查方法：

```bash
# 在服务器上
cd /tmp && rm -rf verify && mkdir verify
tar xzf /opt/backups/tl-backup-$(date +%F).tar.gz -C verify
ls verify/content/products | wc -l     # 应该是 42
python3 -c "import yaml,glob; [yaml.safe_load(open(p)) for p in glob.glob('verify/content/products/*.yaml')]; print('ok')"
```

2026-11-17 验证结果：42 产品 / 6 FAQ / 13 订单 / 4 账号，从备份重建成功。

---

## 七、密钥

**永远不要提交的东西**：

```
Stripe 密钥        sk_test_ / sk_live_ / pk_*
服务器密码
SMTP 密码
SSH 私钥
API token（dop_v1_ / ghp_ / gh[oprsu]_）
```

它们都在服务器的环境变量文件里：

```
/etc/tl-api.env     Stripe、内容服务密钥
/etc/tl-mail.env    SMTP
```

代码里只 `process.env.XXX` 读取，不硬编码。

如果怀疑提交过密钥：

```bash
git log --all --oneline -G "sk_live_[A-Za-z0-9]{20,}"
```

有输出就要立刻去 Stripe 后台轮换密钥——**历史里的密钥就算删掉文件也还在 commit 里**。

---

## 八、常用命令

```bash
# 看最近改了什么
git log --oneline -10
git log --oneline -- content/products/actsep-cd3-cd28.yaml

# 看某个文件的历史
git log -p -- content/site.yaml | head -60

# 查某次提交改了什么
git show <hash> --stat

# 找是哪次提交引入了某个字符串
git log --all --oneline -S "要搜的字符串"

# 看当前和某个 tag 的差异
git diff v2026.11.17 --stat
```

---

## 九、一条经验

这个项目最大的版本管理风险不是「提交写得不好」，而是**内容和代码两条线各走各的**。

代码有 git 兜底，内容只有备份。所以：

> 改完内容（在后台），如果那批改动很重要，隔天确认一次它进了 git。

可以手动，也可以等自动化（给服务器写权限后每天自动同步）。
