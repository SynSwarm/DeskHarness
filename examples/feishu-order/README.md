# examples/feishu-order/

飞书 Bot + 订单查询 — **Phase 4 计划**端到端 Demo（v0.1.0 尚未交付）。

## 当前可用替代

v0.1.0 已可验证同源能力，无需等飞书 Shell：

| 能力 | v0.1.0 入口 |
|------|-------------|
| 渠道接入 | `webhook-generic` Shell · `POST /shells/webhook-generic/inbound` |
| 订单查询 | `order-lookup` 插件（sync-http）· 见 [`examples/minimal/README.md`](../minimal/README.md) |
| 路由 | `configs/routes.yaml` |

## Phase 4 目标组件

- `plugins/feishu-bot` — 飞书 Shell（manifest 占位，待实现）
- `plugins/order-lookup` — 订单查询插件（sync-http 已可用）
- `configs/routes.yaml` — R 层路由

完整 walkthrough 见 [`doc/roadmap/phase-plan.md`](../../doc/roadmap/phase-plan.md) Phase 4。
