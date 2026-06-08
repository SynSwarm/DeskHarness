# 插件 TPAVR 设计指南（L1～L2）

> 上级：[architecture.md](../architecture/architecture.md) §8

## L1 五元素（插件 handler 内）

| 元素 | 形态 |
|------|------|
| **T** | manifest `commands[].target` |
| **P** | `state_machine.py` |
| **A** | `actions/` |
| **V** | `verification.evidence` |
| **R** | 纯函数 route；**不在 V 里跳转** |

## 目录

```
plugins/<plugin_id>/
├── manifest.yaml
├── handler.py          # execute(PluginCommand) -> PluginResult
├── state_machine.py
├── verification.py
└── tests/
```

## manifest

```yaml
plugin_id: order-lookup
commands:
  - name: query
    target: "返回订单可读状态"
    success_criteria: "evidence.status != null"
verification:
  mode: rule_verify
```

## 红线

- 返回 **PluginResult.verification**，禁止 `{ok:true}` 完事
- **禁止** handler 内 dispatch 下一插件 — **R** 在 Engine routes
