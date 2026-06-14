# order-lookup 插件

订单查询示例 — **v0.1.0 已交付**（sync-http 模式）。

## 用法

1. 在 `routing.allowed_plugins` 中加入 `order-lookup`
2. 启动 mock 服务：`python examples/minimal/mock_order_lookup_server.py`
3. manifest 中配置 `execution.mode: sync-http` 与 endpoint URL
4. invoke 示例见 [`examples/minimal/README.md`](../../examples/minimal/README.md)

飞书端到端 Demo 计划见 Phase 4 [`examples/feishu-order/`](../../examples/feishu-order/README.md)。

L1 TPAVR 结构见 [`doc/extension/plugin-tpavr-guide.md`](../../doc/extension/plugin-tpavr-guide.md)。
