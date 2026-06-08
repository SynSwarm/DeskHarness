# 协议规范（OpenHarness + Engine 内部契约）

> **真源**：Shell ↔ Engine 线协议以 **[OpenHarness](https://github.com/SynSwarm/OpenHarness)** 为准。  
> **不另造品牌词**：不使用 DeskEnvelope 等独立命名；Engine 与 Brain / 插件之间用 **BrainRequest**、**PluginCommand** 等 **角色名 + Request/Response** 即可。  
> **TPAVR**：[architecture.md](../architecture/architecture.md) §8

---

## 1. 协议分层

| 链路 | 协议 | 说明 |
|------|------|------|
| **Shell → Engine → Shell** | **OpenHarness** | 对外唯一线格式；`invoke` / health |
| **Engine → Brain → Engine** | BrainRequest / BrainResponse | Engine 内部；Brain 无渠道字段 |
| **Engine → 插件 → Engine** | PluginCommand / PluginResult | Engine 内部；插件不解析 NLU |

```text
Shell ── OpenHarness ──► Engine ── BrainRequest ──► 大脑引擎
                              ◄── BrainResponse ──┘
                         ── PluginCommand ──► 插件
                              ◄── PluginResult ───
                         ── OpenHarness ──► Shell
```

---

## 2. OpenHarness（Shell ↔ Engine）

DeskHarness Engine 暴露标准 OpenHarness 入口（实现阶段）：

- `GET /openharness/health`
- `POST /openharness/invoke`

字段与语义 **以 OpenHarness 仓库 `PROTOCOL.md` 为准**；DeskHarness 不 fork 第二套 Shell 载荷。

### 2.1 DeskHarness 侧映射（摘要）

| OpenHarness | Engine 行为 |
|-------------|-------------|
| `protocol_version` | 版本校验 |
| `request.context` | 洗净后 → BrainRequest.input |
| `correlation_id` | ↔ `trace_id` 双键日志 |
| session / conversation 键 | ↔ `session_id` |
| `action_directives`（若有） | 与 BrainResponse.plan.steps 对齐 |
| 响应中的 Shell 展示字段 | Engine 组装 outbound |

> 契约测试金样：`schemas/openharness/fixtures/minimal-request.json`。

### 2.2 Shell 规则

- Shell **只**采集意图、渲染 Engine 响应
- **禁止** Shell 直连大脑引擎或插件
- 飞书 / IM：**仅 Shell**；智能与路由以 Engine 为唯一真源

---

## 3. BrainRequest / BrainResponse（大脑引擎）

Engine 与 **大脑引擎** 之间专用契约；**不**使用 OpenHarness 包裹，避免 Brain 感知渠道。

### BrainRequest

```json
{
  "request_version": "0.2",
  "trace_id": "tr_01HXYZ...",
  "turn_id": "turn_01HXYZ...",
  "session_id": "sess_01HXYZ...",
  "input": { "type": "text", "text": "帮我查一下订单 12345" },
  "context": {
    "recent_turns": [],
    "session_vars": {}
  },
  "available_intents": ["order.query", "order.cancel", "general.chat"]
}
```

### BrainResponse（T + P）

```json
{
  "response_version": "0.2",
  "trace_id": "tr_01HXYZ...",
  "decision": {
    "target": {
      "statement": "用户获知订单 12345 的最新物流状态",
      "success_criteria": "evidence.status in ['shipped','delivered']"
    },
    "intent": "order.query",
    "confidence": 0.95,
    "entities": { "order_id": "12345" },
    "plan": {
      "mode": "single",
      "steps": [
        {
          "plugin_id": "order-lookup",
          "command": "query",
          "params": { "order_id": "12345" }
        }
      ]
    },
    "reply": { "type": "text", "text": "正在为您查询订单 12345..." }
  }
}
```

| 字段 | TPAVR | 说明 |
|------|-------|------|
| `target` | **T** | `statement` 必填 |
| `plan.steps` | **P** | 有序插件步骤；Fat 引擎可升维为 SOP 图 |
| `confidence` | **V_pre** | 低置信 → Engine **R** fallback |

**Brain 输出规则**

1. `general.chat` 且 `plan.steps` 空 → 仅 `reply`，不调插件  
2. `plan.steps` 非空 → Engine 白名单校验 `plugin_id` 后 dispatch  
3. Brain **禁止** A/V/R（不执行插件、不读 PluginResult 做路由）

---

## 4. PluginCommand / PluginResult（插件）

OSS 以 HTTP / sync-http / local-script 为 Thin 插件形态。

### PluginCommand（纯 A）

```json
{
  "command_version": "0.2",
  "trace_id": "tr_01HXYZ...",
  "turn_id": "turn_01HXYZ...",
  "plugin_id": "order-lookup",
  "command": "query",
  "params": { "order_id": "12345" },
  "session_vars": {}
}
```

### PluginResult（V 证据）

```json
{
  "result_version": "0.2",
  "trace_id": "tr_01HXYZ...",
  "status": "success | failure | partial",
  "verification": {
    "passed": true,
    "evidence": {
      "order_id": "12345",
      "status": "shipped",
      "eta": "2026-06-08"
    },
    "checks": [{ "name": "order_exists", "passed": true }],
    "failure_reason": null
  },
  "error": null,
  "reply_override": null
}
```

**红线**：插件 **不得** 在 Result 后触发下一 Command；**R** 由 Engine `routes.yaml` 读 `verification` 求值（**V 与 R 分离**）。

---

## 5. 版本与 Schema

| 变更 | 策略 |
|------|------|
| OpenHarness 上游变更 | adapter 版本化；不私改 OH 字段名 |
| Brain/Plugin 契约 | 独立 `request_version` / `result_version` |
| 必填字段变更 | 大版本 + ADR |

**工件（v0.2 / OH-1）**

- [x] `schemas/openharness/`（invoke + fixtures，OH-1 金样）
- [x] `schemas/brain-request.v0.2.json`
- [x] `schemas/brain-response.v0.2.json`
- [x] `schemas/plugin-command.v0.2.json`
- [x] `schemas/plugin-result.v0.2.json`

---

## 6. 关联文档

- [路由（R 层）](./routing-intent.md)
- [会话与状态](./session-state.md)
- [架构 · TPAVR](../architecture/architecture.md) §8
