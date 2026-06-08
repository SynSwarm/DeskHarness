# ADR-004: Engine 运行时选用 Python

## 状态

Accepted · 2026-06-07

## 背景

Phase 1 需实现 `deskharness serve`、OpenHarness HTTP 端点、Session、Brain 客户端与插件 dispatch。需在 **Go** 与 **Python** 中选定唯一 Engine 实现语言，避免双栈维护。

约束：

- SME 轻量部署（单进程、embedded SQLite、HTTP）
- 契约以 JSON Schema + Pydantic 友好类型为主
- 插件作者以 sync-http / Python handler 为主
- 与现有 Harness 产品线技术栈可平滑升级（内部见 `doc/private/`）

## 决策

**Engine 实现语言：Python 3.11+**

| 层次 | 选型 |
|------|------|
| HTTP / OH API | **FastAPI** + Uvicorn |
| DTO / 校验 | **Pydantic v2**（对齐 `app/schemas/` 与 `schemas/*.json`） |
| 配置 | **PyYAML** + `configs/*.yaml` |
| Brain / 插件 HTTP | **httpx** |
| Session KV | **SQLite**（stdlib `sqlite3` 或 `aiosqlite`，Phase 1 可同步） |
| CLI | **`deskharness`** 入口 → `cmd/deskharness/` |
| 测试 | **pytest** + JSON Schema 校验（`jsonschema`） |

目录布局不变：`app/` + `core/` + `cmd/` + `pkg/`（`pkg/` 为可安装包命名空间，如 `deskharness.openharness`）。

## 备选方案

| 方案 | 不选原因 |
|------|----------|
| **Go** | 性能更好，但与插件生态（Python handler、脚本类插件）分裂；OH/Brain 契约仍需双份类型定义 |
| **Go Engine + Python 插件 subprocess** | 复杂度高，Phase 1 不必要时延 |

## 后果

- 依赖 `pyproject.toml` 管理；发布形态为 `pip install` 或 venv + `deskharness serve`
- 性能上限低于 Go；MVP 与 SME 场景足够，热点后再评估 Rust/Go 子模块
- 插件 **sync-http** 与 **local-script** 与 Engine 同语言，降低二次开发成本

## Phase 1 落地顺序

1. `pyproject.toml` + FastAPI `app/factory.py`（Composition Root）
2. `POST /openharness/invoke` stub + 金样 roundtrip
3. `tests/contract/openharness/` pytest
4. Session SQLite → Brain client → Router → noop dispatch

## 回滚

若 Phase 1 中期遇阻塞（如并发/部署硬指标），可另开 ADR 评估 Go 重写 **core/** 薄层；**契约与 `schemas/` 不变**，Shell/插件 HTTP 边界不受影响。
