# 版本发布清单

面向维护者：发布 **v0.1.0**（及后续 semver tag）前的检查与操作步骤。

---

## 发布物

| 产物 | 坐标 / 地址 |
|------|-------------|
| Python 包 | `deskharness==0.1.0`（`pyproject.toml`） |
| Git tag | `v0.1.0` |
| Docker 镜像 | `ghcr.io/synswarm/deskharness:0.1.0` · `:latest` |
| GitHub Release | [Releases](https://github.com/SynSwarm/DeskHarness/releases) |

---

## 发布前检查

### 1. 代码与测试

```bash
pip install -e ".[dev]"
pytest tests/ -q
# 期望：29 passed, 1 skipped（Redis 可选）
```

### 2. 版本号一致

| 文件 | 字段 |
|------|------|
| `pyproject.toml` | `[project] version = "0.1.0"` |
| Git tag | `v0.1.0`（带 `v` 前缀） |
| `CHANGELOG.md` | `## [0.1.0]` 条目已更新 |

### 3. 文档

- [ ] `README.md` / `README.zh-CN.md` 状态与路线图反映 Phase 3 完成
- [ ] `PROGRESS.md` 与 `doc/roadmap/phase-plan.md` 已同步
- [ ] `CHANGELOG.md` 含本版本变更摘要
- [ ] `doc/deployment/docker.md` 镜像 tag 示例正确
- [ ] GitHub About：Description + Topics 见 [`doc/deployment/github-about.md`](./github-about.md)

### 4. Docker 本地验证（可选）

```bash
docker compose -f examples/minimal/docker-compose.yml up --build -d
curl -fsS http://127.0.0.1:8080/openharness/health
docker compose -f examples/minimal/docker-compose.yml down
```

### 5. CI

- [ ] `main` 分支最新 commit 通过 **Docker build** workflow
- [ ] 无未合并的发布阻断项

---

## 发布步骤

### Step 1 — 合并并确认 main 干净

```bash
git checkout main
git pull origin main
pytest tests/ -q
```

### Step 2 — 打 tag 并推送

```bash
git tag -a v0.1.0 -m "DeskHarness v0.1.0 — Thin Engine Phase 0–3"
git push origin v0.1.0
```

推送 tag 后自动触发 [`.github/workflows/docker-publish.yml`](../../.github/workflows/docker-publish.yml)：
- 平台：`linux/amd64`、`linux/arm64`
- 标签：`0.1.0`、`0.1`、`latest`

### Step 3 — GHCR 包可见性（首次）

1. 打开 GitHub 仓库 → **Packages** → `deskharness`
2. **Package settings** → **Change visibility** → **Public**
3. 确认组织 `SynSwarm` 允许 Actions 写入 GHCR（默认 `GITHUB_TOKEN` 即可）

### Step 4 — 创建 GitHub Release

```bash
gh release create v0.1.0 \
  --title "v0.1.0 — Thin Engine" \
  --notes-file CHANGELOG.md
```

或于 GitHub UI：**Releases → Draft a new release**，选择 tag `v0.1.0`，正文粘贴 `CHANGELOG.md` 中 `[0.1.0]` 段落。

### Step 5 — 发布后验证

```bash
# Docker
docker pull ghcr.io/synswarm/deskharness:0.1.0
docker run --rm -p 8080:8080 ghcr.io/synswarm/deskharness:0.1.0 &
sleep 5 && curl -fsS http://127.0.0.1:8080/openharness/health

# Compose（仅拉镜像）
DESKHARNESS_TAG=0.1.0 docker compose -f examples/minimal/docker-compose.image.yml up -d
```

---

## 发布后

1. 更新 `PROGRESS.md` 发布日期（如需要）
2. 在 README 添加 Release badge（可选）：
   `![Release](https://img.shields.io/github/v/release/SynSwarm/DeskHarness)`
3. 开启 Phase 4 里程碑（`feishu-order` Demo）

---

## 回滚

| 场景 | 操作 |
|------|------|
| 镜像有问题 | 在 GHCR 保留旧 tag；用户 pin `0.1.0` 而非 `latest` |
| 需撤 tag | `git push origin :refs/tags/v0.1.0`（慎用；已拉取用户不受影响） |
| 热修复 | 发布 `v0.1.1`，更新 CHANGELOG，重新跑 publish workflow |

---

## 相关

- [CHANGELOG.md](../../CHANGELOG.md)
- [Docker 部署](./docker.md)
- [phase-plan.md](../roadmap/phase-plan.md)
