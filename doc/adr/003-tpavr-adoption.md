# ADR-003: T/P/A/V/R 分形元规则深度吸收

## 状态

Accepted · 2026-06-07

## 背景

T/P/A/V/R 作为系统级公理，须在 **协议字段与评审门禁** 中落地。此前仅在术语表做浅层映射（intent→T、routes→R），存在：

- Brain/插件 契约无法表达 **T** 与结构化 **V**
- Engine 路由与插件内部路由混淆（V/R 合并风险）
- 插件作者无 L1 指南，易出现巨型 handler 反模式

## 决策

### 1. 升格为叙事脊梁

`doc/architecture/architecture.md` 为 **TPAVR 与架构唯一公开真源**（§8），优先级高于零散描述。

### 2. 协议升维（目标态）

| 契约 | 变更 |
|------|------|
| BrainResponse | 增加 `target` + `plan`；`action_plan` 作为兼容别名 |
| PluginResult | 增加必填 `verification { passed, evidence, checks }` |
| routes.yaml | 明确为 **R 层**；`when` 只读 verification 证据 |
| Turn | 定义为 **L3** 尺度 SAEV 容器 |

Phase 1 可渐进：先 `verification` + `target.statement`，后 success_criteria 与 brain_verify。

### 3. 分层红线

- Brain：**T+P only**
- 插件：**A+V only**
- Engine：**R only**（+ 验收代理触发）
- Shell：**无 TPAVR**

### 4. 评审门禁

- Architect / QA **5 问**（architecture §12）
- 反模式表（§11）一票否决
- 插件合入须对照 `plugin-tpavr-guide.md`

### 5. Fat 引擎尺度（内部）

L3 Turn 与商用 SOP Run 同公理等 — 见 **`doc/private/`** §5。

## 后果

- 协议 JSON 略增；可测试性、可审计性提升
- v0.1 → schema v0.2（含 adapter）

## 执行清单

- [x] `doc/architecture/architecture.md`（含 TPAVR §8）
- [x] `plugin-tpavr-guide.md`
- [x] `openharness-protocol.md`
- [x] `schemas/` v0.2 + OH 金样
- [ ] Engine Router `when` 求值（Phase 1）
