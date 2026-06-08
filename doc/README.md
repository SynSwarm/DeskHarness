# DeskHarness 文档索引

开源 **Thin Harness Engine** — OpenHarness + TPAVR + 插件。

## 阅读顺序

| 顺序 | 文档 | 说明 |
|------|------|------|
| 1 | **[架构](./architecture/architecture.md)** | **必读** · 独立完整 |
| 2 | [OpenHarness 协议](./specs/openharness-protocol.md) | Shell↔Engine + Engine 内部契约 |
| 3 | [会话与状态](./specs/session-state.md) | |
| 4 | [路由（R 层）](./specs/routing-intent.md) | |
| 5 | [扩展点](./extension/extension-points.md) | |
| 6 | [插件 TPAVR（L1）](./extension/plugin-tpavr-guide.md) | |
| 7 | [仓库结构 · STRUCTURE.md](../STRUCTURE.md) | |
| 8 | [路线图](./roadmap/phase-plan.md) | Phase 1–2 ✅ · Phase 3 下一步 |
| — | [ADR-003](./adr/003-tpavr-adoption.md) · [ADR-004 Python](./adr/004-python-runtime.md) | |
| — | [`PROGRESS.md`](../PROGRESS.md) | 实现进度与本地验证命令 |

> 旧链 [desk-envelope.md](./specs/desk-envelope.md) 已废弃。

## 一句话

**OpenHarness 接线 + TPAVR + 插件** — Engine 不思考、不执行业务，只路由与持 Session。
