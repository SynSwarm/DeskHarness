# DeskHarness 进度与任务

最后更新：2026-06-07 · **准备发布 v0.1.0**

## 当前阶段

**Phase 3 — 生产就绪 ✅ · 即将发布 v0.1.0 · Phase 4 下一步**

---

## 发布清单（v0.1.0）

| 步骤 | 状态 |
|------|------|
| Phase 0–3 功能完成 | ✅ |
| `pytest tests/ -q`（29 passed, 1 skipped） | ✅ |
| `CHANGELOG.md` | ✅ |
| 官方 Docker + CI publish workflow | ✅ |
| 打 tag `v0.1.0` 并 push | ⬜ |
| GHCR 包设为 Public | ⬜ |
| GitHub Release 创建 | ⬜ |

详细步骤见 [`doc/deployment/release.md`](doc/deployment/release.md)。

```bash
git tag -a v0.1.0 -m "DeskHarness v0.1.0 — Thin Engine Phase 0–3"
git push origin v0.1.0
gh release create v0.1.0 --title "v0.1.0 — Thin Engine" --notes-file CHANGELOG.md
```

---

## Phase 1 ✅ · Phase 2 ✅

见 [`CHANGELOG.md`](CHANGELOG.md) 与 git 历史。

---

## Phase 3 ✅

| ID | 任务 | 状态 |
|----|------|------|
| P3-0 | 结构化日志 `memory/logs/turns.jsonl` | ✅ |
| P3-1 | `/metrics` Prometheus 计数 | ✅ |
| P3-2 | Session Redis 后端（可选 `pip install deskharness[redis]`） | ✅ |
| P3-3 | sync-http 插件 dispatch | ✅ |
| P3-4 | `/debug/routes` · `/debug/dry-run` | ✅ |
| P3-5 | mock order-lookup HTTP 示例 | ✅ |
| P3-6 | 集成测试 | ✅ 29 passed |
| P3-7 | async-webhook + `/plugins/callbacks/{task_id}` | ✅ |
| P3-8 | local-script 超时 / subprocess 沙箱 | ✅ |
| P3-9 | Context summarization | ✅ |
| P3-10 | Rate limit | ✅ |
| P3-11 | 官方 Docker 镜像（GHCR + CI） | ✅ |

---

## 本地验证

```bash
pip install -e ".[dev]"
pytest tests/ -q
deskharness serve
curl -s localhost:8080/openharness/health
curl -s localhost:8080/metrics
```

Docker：

```bash
docker compose -f examples/minimal/docker-compose.yml up --build
```

完整命令见 [`examples/minimal/README.md`](examples/minimal/README.md)。

---

## 下一步（Phase 4）

- `examples/feishu-order/` 飞书 + 订单查询端到端 Demo
- `feishu-bot` / `telegram-bot` Shell
- MkDocs 文档站

见 [`doc/roadmap/phase-plan.md`](doc/roadmap/phase-plan.md)。
