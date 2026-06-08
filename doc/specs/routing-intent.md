# 路由与意图（R 层 · TPAVR）

Engine 在收到 BrainResponse（**T+P**）并完成插件（**A**）、收集 PluginResult（**V**）后，根据 **routes.yaml** 做 **R 求值**。

> **真源**：[architecture.md](../architecture/architecture.md) §8 · **红线**：V 与 R 不得合并；Router **只读** `verification` 证据，不在插件内路由。

---

## 1. 路由决策流程（SAEV 后半段）

```
BrainResponse (T+P)
      │
      ▼
┌─────────────────┐
│ confidence V_pre│──No──► fallback (R)
└────────┬────────┘
         │ Yes
         ▼
┌─────────────────┐
│ plan.steps 空？  │──Yes──► completed (仅 reply)
└────────┬────────┘
         │ No
         ▼
┌─────────────────┐
│ Dispatch A      │
└────────┬────────┘
         ▼
┌─────────────────┐
│ PluginResult V  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ routes.yaml R   │──► 下一 A / outbound / 验收代理
└─────────────────┘
```

---

## 2. 路由规则配置

`routes.yaml` 示例：

```yaml
routes:
  - match:
      intent: order.query
    when: "$verification.evidence.status != null"
    plugin:
      plugin_id: order-lookup
      command: query
      param_mapping:
        order_id: "$entities.order_id"

  - match:
      intent: order.query
    when: "$verification.passed == false"
    reply:
      text: "未找到该订单，请核对订单号。"
    plugin: null

  - match:
      intent: order.cancel
    plugin:
      plugin_id: order-lookup
      command: cancel
      param_mapping:
        order_id: "$entities.order_id"
      require_confirmation: true

  - match:
      intent: general.chat
    plugin: null

  - match:
      intent: system.unknown
    plugin:
      plugin_id: noop
    reply:
      text: "抱歉，我没有理解您的意思，请换个说法试试。"

fallback:
  on_brain_timeout:
    reply: "系统繁忙，请稍后再试。"
  on_brain_error:
    reply: "处理出现问题，请稍后重试。"
  on_plugin_failure:
    strategy: read_verification   # R 读 V 证据，不硬编码文案
  on_target_unmet:
    strategy: brain_verify          # 验收代理：Brain 读 V 判 T.success_criteria
```

---

## 3. 匹配优先级

1. **精确 intent 匹配**
2. **前缀匹配**（`order.*` → `order-lookup`）
3. **fallback 规则**
4. **全局 default**（未匹配 → `system.unknown`）

```yaml
routes:
  - match:
      intent: "order.*"
      priority: 10
    plugin:
      plugin_id: order-lookup
```

---

## 4. plan.steps 与 routes 的关系

| 模式 | 行为 |
|------|------|
| `brain_led`（默认） | 大脑引擎输出 plan.steps，Engine 校验 plugin_id 白名单 |
| `route_led`（可选） | Engine 仅按 intent 查 routes |

```yaml
routing:
  mode: brain_led
  allowed_plugins:
    - order-lookup
    - noop
```

---

## 5. 多插件编排

```json
"plan": {
  "steps": [
    { "plugin_id": "user-lookup", "command": "get", "params": { "user_id": "u1" } },
    { "plugin_id": "order-lookup", "command": "query", "params": { "order_id": "12345" } }
  ]
}
```

Engine 串行 dispatch；**R** 读每步 PluginResult.verification。

---

## 6. 条件路由（Phase 3）

```yaml
routes:
  - match:
      intent: order.query
      when: "$session_vars.user_tier == 'vip'"
    plugin:
      plugin_id: order-lookup-vip

  - match:
      intent: order.query
    plugin:
      plugin_id: order-lookup
```

`when` 表达式为轻量 DSL，非 Turing-complete。

---

## 7. Brain 与路由表的协同

Engine 启动时将 `available_intents` 注入 BrainRequest：

```yaml
routing:
  export_intents_to_brain: true
  intent_descriptions:
    order.query: "用户想查询订单状态"
    order.cancel: "用户想取消订单"
    general.chat: "普通闲聊"
```

Brain 实现者可据此做 function calling 或 prompt 约束，提高 intent 命中率。

---

## 8. 路由调试

开发模式下 Engine 暴露（仅 localhost）：

```
GET /debug/routes
POST /debug/dry-run            # BrainResponse → 将 dispatch 的 plugin
```
