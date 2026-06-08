# DeskHarness 进度与任务

最后更新：2026-06-07 · **Phase 2 收束，暂停于 Phase 3 前**

## 当前阶段

**Phase 2 — 插件体系 ✅** · 下一步 **Phase 3 生产就绪**

---

## Phase 1 ✅

| 范围 | 交付 |
|------|------|
| P1-0 ~ P1-7 | OH invoke · SQLite Session · Brain client · routes.yaml · noop dispatch · 契约测试 |

---

## Phase 2 ✅

| ID | 任务 |
|----|------|
| P2-0 ~ P2-6 | manifest · PluginRegistry · pkg SDK · noop/echo · webhook Shell · 集成测试 |
| P2-7 | `prompt-template` Brain · `configs/brain.prompt-template.yaml` |
| P2-8 | `deskharness plugin new` |
| P2-9 | `examples/minimal/` Dockerfile + docker-compose |

---

## Phase 3（未开始）

Redis KV · sync-http 插件 · structured logging · metrics · `/debug/dry-run` — 见 [`doc/roadmap/phase-plan.md`](doc/roadmap/phase-plan.md)

---

## 本地验证

```bash
pip install -e ".[dev]"
pytest tests/ -q          # 18 passed
deskharness serve

curl -s localhost:8080/openharness/health
curl -s -X POST localhost:8080/shells/webhook-generic/inbound \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hello","session_id":"sess_demo"}'

docker compose -f examples/minimal/docker-compose.yml up --build
deskharness plugin new demo-bot --type plugin
```

Stub 契约模式：`DH_OPENHARNESS_STUB_MODE=minimal_200` 或 `engine.openharness.invoke_mode: stub`
