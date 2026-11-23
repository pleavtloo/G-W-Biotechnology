# P00 · 仓库初始化与基线校验

**目标**：让一个新克隆的仓库能在 5 分钟内跑起来，并确认基线是绿的。

**前置**：无。这是第一轮。

**先读**：`CODEBUDDY.md`、`codebuddy/README.md`

---

## 任务

1. 确认目录结构符合 `CODEBUDDY.md` 第 4 节。缺的目录建空目录并加 `.gitkeep`。
2. 检查 `.gitignore` 是否包含：`.venv/`、`dist/`、`shots/`、`server/outbox/`、
   `server/.dev.vars`、`__pycache__/`、`*.pyc`。缺的补上。
3. 逐条跑下面四条命令，把**原始输出**贴回来：
   ```bash
   python tools/build_site.py
   python tools/build_docs.py
   python tools/build_dist.py
   python tools/check.py
   ```
4. 如果 `check.py` 不是 PASS，先修到 PASS。只修检查报出来的问题，不要顺手改别的。
5. 写 `Makefile`（或在 `README` 里加一节），提供四个命令：
   `make build` / `make dist` / `make check` / `make dev`。

## 约束

- 不改任何页面文案、不改 CSS、不改设计。
- 不新增依赖。`build_docs.py` 依赖 `fpdf2`，如果缺就说明需要 `pip install fpdf2`，不要换库。
- 不改 `dist/` 里的任何文件（它是产物）。

## 验收

```bash
python tools/check.py     # 必须输出 PASS
```

期望输出形如：

```
dist: 12 pages

PASS - 48 hard checks clean
```

## 交付

- 补齐的目录与 `.gitignore`
- `Makefile`（或 README 中的命令表）
- 四条命令的原始输出
- 如果修了 check 报的问题，逐个说明改了什么
