# webhook-generic Shell

通用 HTTP Webhook Shell — **v0.1.0 已交付**。

## 入口

```bash
POST /shells/webhook-generic/inbound
Content-Type: application/json

{"text": "Hello from webhook", "session_id": "sess_demo"}
```

Engine 将 payload 转为 OpenHarness invoke，走完整 Turn 闭环后返回 JSON 回复。

## 配置

在 `configs/routes.yaml` 与 `engine.plugin_dirs` 中启用；rate limit 可作用于 shell inbound 路径。

示例见 [`examples/minimal/README.md`](../../examples/minimal/README.md)。
