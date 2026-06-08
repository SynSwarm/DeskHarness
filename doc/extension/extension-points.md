# 扩展点与二次开发指南

> Shell 与 **插件** 均在 **`plugins/<plugin_id>/` 扁平目录**；协议见 [openharness-protocol.md](../specs/openharness-protocol.md)。  
> 目录真源：[STRUCTURE.md](../../STRUCTURE.md)。

## 1. 扩展点

| 扩展点 | 目录 | 区分方式 | 难度 |
|--------|------|----------|------|
| Shell | `plugins/<shell-id>/` | `plugin_type: shell` | ⭐⭐ |
| 业务插件 | `plugins/<plugin-id>/` | `plugin_type: plugin` | ⭐⭐ |
| 大脑引擎 | HTTP 服务 + `configs/brain.yaml` | — | ⭐⭐⭐ |
| 路由 R | `configs/routes.yaml` | — | ⭐ |

## 2. Shell 插件

```yaml
plugin_id: feishu-bot
plugin_type: shell
version: 1.0.0
entry: adapter:FeishuShell
capabilities:
  inbound_types: [text, event]
  outbound_types: [text, rich]
```

| 方法 | 职责 |
|------|------|
| `to_invoke_request(raw)` | 渠道 → OpenHarness request |
| `from_invoke_response(resp)` | OH 响应 → 渠道 API |

## 3. 业务插件

```yaml
plugin_id: order-lookup
plugin_type: plugin
execution:
  mode: sync-http
commands:
  - name: query
    target: "返回订单可读状态"
    params_schema: schemas/query.json
verification:
  mode: rule_verify
exports:
  - from: evidence.order_id
    to: session_vars.last_order_id
```

L1 结构见 [plugin-tpavr-guide.md](./plugin-tpavr-guide.md)。

## 4. 大脑引擎

`configs/brain.yaml` / `configs/config.yaml` — 适配器：

| adapter | 说明 |
|---------|------|
| `mock` | 内置关键词路由（开发默认） |
| `http` | POST 外置 Brain 服务 |
| `prompt-template` | YAML 规则模板，零 LLM（`configs/brain.prompt-template.yaml`） |

Brain 输出须含 **target + plan**（T+P）。

## 5. 插件发现

```yaml
# configs/config.yaml
engine:
  plugin_dirs:
    - ./plugins
```

启动时 `core/plugin_loader.py` 加载 manifest；业务插件需 `handler.py`，Shell 需 `adapter.py`。

```bash
deskharness plugin new my-bot --type plugin
deskharness plugin new my-webhook --type shell
```

## 6. 合入自检（5 问）

见 [architecture.md §12](../architecture/architecture.md#12-评审-5-问强制)。
