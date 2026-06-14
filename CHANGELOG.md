# Changelog

All notable changes to DeskHarness are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).  
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-07

First public release — **Thin Harness Engine** production-ready (Phase 0–3).

### Added

**Engine core (Phase 1)**

- OpenHarness `GET /health` and `POST /invoke` with protocol validation
- Turn loop: Session → Brain → Router → Plugin → outbound
- Embedded SQLite session store with TTL
- Mock and HTTP Brain clients
- `routes.yaml` brain-led routing (R layer)
- `deskharness serve` CLI

**Plugin system (Phase 2)**

- Plugin loader from `plugins/<id>/manifest.yaml`
- Execution modes: `local-script`, `sync-http`, `async-webhook`, `in-process`
- Shell API: `POST /shells/webhook-generic/inbound`
- Built-in plugins: `noop`, `echo`, `order-lookup`, `async-demo`
- Built-in shell: `webhook-generic`
- `prompt-template` Brain adapter (rule-based, no LLM)
- `deskharness plugin new` scaffold CLI
- `examples/minimal/` docker compose demo

**Production readiness (Phase 3)**

- Structured turn logging → `memory/logs/turns.jsonl`
- Metrics: `GET /metrics` (Prometheus) and `/metrics/json`
- Optional Redis session backend (`pip install deskharness[redis]`)
- sync-http plugin dispatch with mock order-lookup example
- async-webhook dispatch + `GET/POST /plugins/callbacks/{task_id}`
- local-script handler timeout and subprocess sandbox (`execution.sandbox`)
- Session context compaction before Brain calls
- Rate limiting on invoke and shell inbound paths
- Debug API: `/debug/routes`, `/debug/dry-run` (dev + localhost)
- Official Docker image: `ghcr.io/synswarm/deskharness`
- CI: docker build smoke test on PR/main; multi-arch publish on `v*` tags

### Documentation

- Architecture, OpenHarness protocol, routing, extension points
- Plugin TPAVR guide, repo layout (`STRUCTURE.md`), phase roadmap
- Docker deployment and release guides

### Known limitations (v0.1.0)

- Redis KV for full session export not yet complete
- `feishu-order` end-to-end demo planned for Phase 4
- Official image ships without `[redis]` extra; extend Dockerfile for Redis in production
- Rate limit is in-process token bucket (single instance)

---

## Upcoming (Phase 4)

- `examples/feishu-order/` full channel demo
- `feishu-bot` / `telegram-bot` shells
- MkDocs documentation site
- Plugin SDK polish

[0.1.0]: https://github.com/SynSwarm/DeskHarness/releases/tag/v0.1.0
