# Docker 部署

官方镜像托管在 **GitHub Container Registry (GHCR)**。

| 镜像 | 说明 |
|------|------|
| `ghcr.io/synswarm/deskharness:latest` | 最新 semver 发布 |
| `ghcr.io/synswarm/deskharness:0.1.0` | 指定版本 |

---

## 快速运行（已发布镜像）

```bash
docker run -d --name deskharness \
  -p 8080:8080 \
  -v deskharness-sessions:/app/memory/sessions \
  -v deskharness-logs:/app/memory/logs \
  ghcr.io/synswarm/deskharness:latest

curl -s http://127.0.0.1:8080/openharness/health
```

或使用 compose（无需本地 build）：

```bash
docker compose -f examples/minimal/docker-compose.image.yml up -d
```

指定版本：

```bash
DESKHARNESS_TAG=0.1.0 docker compose -f examples/minimal/docker-compose.image.yml up -d
```

---

## 本地构建

仓库根目录 `Dockerfile` 为官方镜像定义；`examples/minimal/docker-compose.yml` 默认 **build + 可选 image 标签**：

```bash
docker compose -f examples/minimal/docker-compose.yml up --build
```

可选 HTTP mock Brain sidecar：

```bash
docker compose -f examples/minimal/docker-compose.yml --profile http-brain up --build
```

---

## 镜像内容

- Python 3.11-slim
- 内置 `noop` / `echo` / `order-lookup` / `async-demo` 等默认插件
- 默认配置：`configs/config.docker.yaml`（`dev_mode: false`，监听 `0.0.0.0:8080`）
- 非 root 用户 `deskharness` (uid 1000)
- 内置 `/openharness/health` HEALTHCHECK

持久化目录：

| 路径 | 用途 |
|------|------|
| `/app/memory/sessions` | embedded SQLite Session |
| `/app/memory/logs` | 结构化 Turn 日志 |

---

## 自定义配置

挂载自己的 `config.yaml`（需包含完整 engine/brain/routing 段）：

```bash
docker run -d --name deskharness \
  -p 8080:8080 \
  -v "$(pwd)/configs/config.yaml:/app/configs/config.yaml:ro" \
  -v deskharness-sessions:/app/memory/sessions \
  ghcr.io/synswarm/deskharness:latest \
  deskharness serve --host 0.0.0.0 --port 8080 --config /app/configs/config.yaml
```

Redis Session（需自定义镜像或扩展 Dockerfile 安装 `[redis]` extra）：

```yaml
engine:
  session:
    backend: redis
    redis_url: redis://redis:6379/0
```

---

## 发布流程（维护者）

完整清单见 **[`doc/deployment/release.md`](../../doc/deployment/release.md)**。

1. 合并到 `main`，确认 `pytest tests/ -q` 通过
2. 打 tag 并推送：`git tag v0.1.0 && git push origin v0.1.0`
3. CI 自动构建 multi-arch 镜像推送到 GHCR
4. 首次：GitHub **Packages** → 设为 Public
5. 创建 GitHub Release（正文见 `CHANGELOG.md`）

```bash
gh release create v0.1.0 --title "v0.1.0 — Thin Engine" --notes-file CHANGELOG.md
```

首次拉取私有包需登录：

```bash
echo "$GITHUB_TOKEN" | docker login ghcr.io -u USERNAME --password-stdin
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| [`Dockerfile`](../../Dockerfile) | 官方 Engine 镜像 |
| [`configs/config.docker.yaml`](../../configs/config.docker.yaml) | 镜像内默认配置 |
| [`.github/workflows/docker-publish.yml`](../../.github/workflows/docker-publish.yml) | 发布 workflow |
| [`.github/workflows/docker-build.yml`](../../.github/workflows/docker-build.yml) | PR/main build 校验 |
| [`doc/deployment/release.md`](./release.md) | 发布清单 |
| [`CHANGELOG.md`](../../CHANGELOG.md) | 版本变更 |
