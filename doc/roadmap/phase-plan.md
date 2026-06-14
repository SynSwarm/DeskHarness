# 阶段路线图

分阶段落地，每阶段有 **可演示的里程碑**，避免大爆炸式开发。

---

## Phase 0 — 体系冻结 ✅

**目标**：架构文档、协议草案、目录约定就绪。

| 交付物 | 状态 |
|--------|------|
| 四层模型 / 架构单篇 | ✅ |
| OpenHarness 协议规范 | ✅ |
| 路由 / 状态 / 扩展点 | ✅ |
| 仓库结构 + Schema v0.2 | ✅ |
| OpenHarness Profile 对照 | ⬜ |
| 技术选型 | ✅ **Python** · [ADR-004](../adr/004-python-runtime.md) |

---

## Phase 1 — Engine MVP ✅

**目标**：跑通最小闭环 `invoke → Session → Brain → noop 插件`。

| 功能 | 状态 |
|------|------|
| OpenHarness invoke 校验 | ✅ |
| Session KV（embedded SQLite） | ✅ |
| Brain HTTP / mock Client | ✅ |
| routes.yaml 路由 | ✅ |
| noop 进程内 dispatch | ✅ |
| `deskharness serve` | ✅ |
| 结构化日志 + trace_id | ✅ Phase 3 |
| Rate limit | ✅ Phase 3 |

**演示**：curl 金样 → mock Brain → noop → outbound JSON。

---

## Phase 2 — 插件体系 ✅

**目标**：Shell / 插件可插拔，无需改 Engine 代码。

| 功能 | 状态 |
|------|------|
| Plugin Loader + manifest | ✅ |
| `webhook-generic` Shell + `/shells/.../inbound` | ✅ |
| `noop` / `echo` 插件 | ✅ |
| `prompt-template` Brain Adapter | ✅ |
| `deskharness plugin new` 脚手架 | ✅ |
| 集成 / 契约测试 | ✅ |
| `examples/minimal/` docker compose | ✅ |
| `feishu-order` 完整 Demo | ⬜ Phase 4 |

**演示**：`docker compose -f examples/minimal/docker-compose.yml up --build`

---

## Phase 3 — 生产就绪 ✅

**目标**：小团队可上生产。

| 功能 | 状态 |
|------|------|
| 结构化日志 + trace_id | ✅ `memory/logs/turns.jsonl` |
| `/metrics` 端点 | ✅ |
| Session Redis 后端 | ✅ 可选 `[redis]` |
| sync-http 插件 dispatch | ✅ |
| `/debug/routes` · `/debug/dry-run` | ✅ |
| mock order-lookup 示例 | ✅ |
| Redis KV（完整） | ⬜ |
| 插件 async-webhook + 回调 | ✅ `plugins/async-demo` · `/plugins/callbacks/{task_id}` |
| 插件 local-script 沙箱 | ✅ 超时 + `execution.sandbox` subprocess |
| Context summarization | ✅ `core/runtime/compaction.py` |
| Rate limit | ✅ `/openharness/invoke` · `/shells/*/inbound` |
| Docker 官方镜像发布 | ✅ `ghcr.io/synswarm/deskharness` |

---

## Phase 4 — 生态与示例（下一步）

**目标**：降低二次开发门槛，形成社区。

| 功能 | 优先级 |
|------|--------|
| `telegram-bot` Shell | P1 |
| `feishu-bot` Shell | P1 |
| `examples/order-bot` 完整业务示例（飞书 + 订单查询） | P0 |
| Python Plugin SDK | P1 |
| 插件 Registry 设计 | P2 |
| 中英文文档站点（MkDocs） | P1 |

---

## Phase 5 — 企业扩展（商用 Fat Engine · 非本仓开源核心）

> Phase 1–4 交付 **Thin Engine**；企业级能力在 **商用产品线** 仓落地，通过扩展叠加，不推翻 Shell–Engine–Brain–插件 边界。

| 功能 | 说明 |
|------|------|
| SopEngine + SOP.json | 插件 Fat 形态 |
| RPA 子系统 | BrowserManager、DeviceManager |
| FCBot + 指挥舱 | 内置呈现面 |
| RBAC / 计费 / 多租户 | Application 治理 |
| OpenHarness invoke 真映射 | 与 OSS Engine OH Profile 兼容 |

开源核心保持 **单租户、Thin Engine、配置驱动**。

---

## 里程碑时间线（示意）

```
2026 Q2   Phase 0 ████████ 体系文档
          Phase 1 ████████████ Engine MVP ✅
          Phase 2 ████████ 插件体系 ✅
2026 Q2   Phase 3 ████████████ 生产就绪 ✅
          v0.1.0 发布 ← 当前
2026 Q3   Phase 4 ████████████████ 生态
2027+     Phase 5 商业扩展（并行）
```

---

## 下一步行动（Phase 4）

1. **`examples/feishu-order/`**：飞书 Bot + 订单查询端到端 Demo（P0）
2. **`feishu-bot` Shell**：替换 webhook-generic 做真实渠道演示
3. **MkDocs 文档站**：架构 + 快速上手 + API 参考
4. **插件 SDK**：完善 `pkg/` 文档与示例

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| 与 LangChain Deep Agents 定位混淆 | 文档明确「Integration Harness vs Agent Harness」 |
| 协议频繁变动 | Phase 0 冻结 v0.1，Breaking 走大版本 |
| SME 仍觉得复杂 | Phase 2 的 minimal example + prompt-template 零代码路径 |
| 插件安全（local-script） | 沙箱 + 权限 manifest，默认关闭 |

发布操作见 [`doc/deployment/release.md`](../deployment/release.md)。
