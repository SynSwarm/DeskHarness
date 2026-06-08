# DeskHarness 架构

> **地位**：开源 Thin Harness Engine 的 **唯一公开架构真源**。  
> **协议细节**：见 [OpenHarness 协议](../specs/openharness-protocol.md)、[路由](../specs/routing-intent.md)、[会话](../specs/session-state.md)。  
> **目录**：见根目录 [STRUCTURE.md](../../STRUCTURE.md)。

---

## 1. 我们要解决什么问题

中小企业做 AI 应用时常见痛点：

- **单体耦合**：换渠道、换模型、加业务能力都要改核心代码  
- **渠道爆炸**：飞书、Telegram、Webhook 各写一套，无法复用 Brain 与插件  
- **模型绑定**：业务逻辑与某一家 LLM SDK 缠在一起  
- **运维过重**：为一个小场景引入 K8s、消息队列、向量库

DeskHarness 提供 **Integration Harness（Thin Engine）**：

**OpenHarness 接线 + Session + 路由（R）+ 插件调度** — 大脑引擎与业务插件可插拔，Engine 本身不思考、不执行业务。

---

## 2. 定位：Harness Engine，不是 Agent 框架

DeskHarness **不是** LangChain / CrewAI / AutoGen 的替代品，而是 **编排与契约层**：

| 角色 | 职责 |
|------|------|
| **大脑引擎** | 推理与 **T+P**（Target + Plan）；默认外置 HTTP，无 Session |
| **插件** | 机械执行 **A+V**（Action + Verify 证据） |
| **Engine** | 协议、Session、**R**（routes）、工具网关、审计 |

Agent 框架回答「怎么让 LLM 思考、调工具」；Harness 回答 **「谁该做什么、用什么契约、状态谁持有、失败怎么降级」**。

---

## 3. 设计原则

| # | 原则 | 说明 |
|---|------|------|
| P1 | **绝对解耦** | Shell / Engine / 大脑引擎 / 插件 — 仅经 OpenHarness 与 Engine 内部契约；禁止跨层直连 |
| P2 | **Headless First** | Engine 无 UI、无业务；Shell 与插件由社区扩展 |
| P3 | **配置优于代码** | `routes.yaml` 为 **R 层**数据声明 |
| P4 | **SME 轻量** | 单进程 + KV（embedded 或 Redis）+ HTTP |
| P5 | **渐进复杂度** | MVP：1 Shell + 1 大脑引擎 + 1 插件 |
| P6 | **Harness 治理** | TPAVR 公理、运行四件套、评审 5 问；禁止 Agent 裸奔 |
| P7 | **尽量不造词** | Shell↔Engine 用 **OpenHarness**；内部用 BrainRequest / PluginCommand 等角色契约 |

---

## 4. 四层模型

```text
 Shell  ── OpenHarness ──►  Engine  ──►  大脑引擎
 (外延)                      (Harness)      (Brain)
                                │
                                └──►  插件 (plugins/)
```

| 层 | 职责 | 代码落点 |
|----|------|----------|
| **Shell** | 采集意图、渲染回复；OpenHarness Shell 侧 | `plugins/<id>/`，`plugin_type: shell` |
| **Engine** | Session/Turn 真源、路由 R、工具网关、Brain 客户端 | `app/` + `core/` |
| **大脑引擎** | BrainRequest → BrainResponse（**T+P**）；无 Session | 外置 HTTP（`configs/brain.yaml`） |
| **插件** | PluginCommand → PluginResult（**A+V**） | `plugins/<plugin_id>/` |

### 4.1 Shell

- `to_invoke_request(raw)` / `from_invoke_response(resp)`  
- **禁止**：直连大脑引擎或插件；持有 Session 业务态  

### 4.2 Engine

| 模块 | 职责 |
|------|------|
| Ingress / Egress | OpenHarness invoke |
| Session | `session_id` 唯一真源；持久化 `memory/sessions/` |
| Router | **R**：`configs/routes.yaml` |
| Dispatcher | 工具网关 → PluginCommand |
| Brain client | BrainRequest / BrainResponse |

**禁止**：业务 Target 定义、LLM 推理、插件业务逻辑。

### 4.3 大脑引擎

- 输出结构化 `intent`、`target`、`plan`  
- **禁止**：执行插件、读 DB、维护 Session、感知渠道来源  

### 4.4 插件

- manifest 声明 `commands`、`verification`、`exports`  
- **禁止**：NLU、LLM、直连 Shell、在 handler 内做 **R**（不决定下一跳）  

### 4.5 层间规则

```text
允许：  Shell ──OH──► Engine ──Brain*──► 大脑引擎
        Engine ──Plugin*──► 插件
禁止：  Shell ──X──► 大脑引擎 / 插件
        大脑引擎 ──X──► 插件
        插件 ──X──► Shell
```

### 4.6 故障隔离

| 故障 | 影响 |
|------|------|
| Shell 挂 | 该渠道不可用 |
| 大脑引擎超时 | 当前 Turn failed；Session 保留 |
| 插件 failed | R 读 verification 降级 |
| Engine 挂 | 全渠道不可用（MVP 单点） |

---

## 5. 术语表

| 术语 | 定义 |
|------|------|
| **Harness（马具）** | 边界 + 契约 + 审计；非安装包名 |
| **Shell** | 外延客户端（飞书、TG、Webhook 等） |
| **Engine** | Harness 服务端；Session / 路由 / Trace 真源 |
| **OpenHarness** | Shell ↔ Engine **线协议**（`/openharness/invoke`） |
| **大脑引擎** | 策略层；输出 T+P |
| **插件** | 执行层；`plugin_id`；目录 `plugins/` |
| **Turn** | 一次 Shell 往返闭环（L3 SAEV 容器） |
| **Session** | Engine 持有；含 `recent_turns`、`session_vars` |
| **BrainRequest / BrainResponse** | Engine ↔ 大脑引擎 |
| **PluginCommand / PluginResult** | Engine ↔ 插件 |
| **routes.yaml** | **R** 层数据声明 |
| **trace_id** | 全链路追踪；可与 OH `correlation_id` 双键日志 |
| **TPAVR** | Target / Plan / Action / Verify / Route 系统公理 |

### 弃用词（历史文档）

| 弃用 | 改用 |
|------|------|
| DeskEnvelope | OpenHarness + BrainRequest / PluginCommand |
| Skin | Shell |
| Action 层 / action_id | 插件 / plugin_id |
| ActionCommand / ActionResult | PluginCommand / PluginResult |

---

## 6. 核心对象

```
Session
├── session_id
├── subject.channel_user_id
├── shell_id
├── context.recent_turns
├── context.session_vars
└── turns[]

Turn
├── turn_id, trace_id, session_id
├── brain_response           # T+P
├── plugin_results[]         # V
├── outbound                 # → OpenHarness 响应
└── status
```

配置入口：

```yaml
configs/config.yaml      # 主配置（模板见 config.template.yaml）
configs/routes.yaml      # R
configs/brain.yaml       # 大脑引擎
```

---

## 7. 核心数据流

```text
Shell ── OpenHarness ──► Engine ── BrainRequest ──► 大脑引擎
                              ◄── BrainResponse ──┘
                         ── PluginCommand ──► 插件
                              ◄── PluginResult ───
                         ── OpenHarness ──► Shell
```

---

## 8. T/P/A/V/R 公理（叙事脊梁）

任何「做事的单元」— 从插件 handler 内部、到一条 PluginCommand、到一次 Turn — 都须能投影回五元素：

| 字母 | 名 | 含义 |
|------|-----|------|
| **T** | Target | 本尺度要到达的状态 |
| **P** | Plan | 达成 T 的方案（图：节点 + 边 + 条件） |
| **A** | Action | **改变**世界状态 |
| **V** | Verify | **读取**世界状态（含证据） |
| **R** | Route | 基于 V 在 P 上选下一节点或终止 |

### 8.1 三条红线

1. **A 改世界，V 读世界** — 不得在同一函数里混编改、读与跳转决策  
2. **V 与 R 不得合并** — 路由必须数据声明（`routes.yaml`），禁止藏在插件 handler 内  
3. **执行者不自证完成** — V 产证据；PASS/FAIL 由 Router 或 **验收代理** 读证据判定  

### 8.2 SAEV 时间投影（Turn · L3）

```
    V_pre  ──►  A  ──►  V_post  ──►  R
   (Brain       (插件)   (PluginResult)   (routes.yaml)
    confidence)
```

Turn 默认：**Brain confidence ≈ V_pre** → dispatch **A** → **PluginResult = V_post** → **Engine R**。

### 8.3 分形尺度

| 尺度 | 名称 | 说明 |
|------|------|------|
| L0 | 原语 SDK | 不适用 TPAVR |
| L1 | 插件 handler 内部 | 见 [插件 TPAVR 指南](../extension/plugin-tpavr-guide.md) |
| L2 | 单条 PluginCommand | 单步 A + V |
| **L3** | **Turn** | **开源主战场** |
| L4 | 多插件 Turn | 串行 plan.steps |
| L5 | Session 工作流 | Phase 3+ |

### 8.4 四层 × TPAVR 归属

| 层 | 允许 | 禁止 |
|----|------|------|
| Shell | — | T/P/A/V/R（仅 OH 转换） |
| Engine | **R**、Turn 级 V 聚合、验收代理 | A、业务 T/P |
| 大脑引擎 | **T**、**P** | A、V、R |
| 插件 | **A**、**V** | R、P（图） |

### 8.5 协议绑定（摘要）

- **BrainResponse**：`target`（T）、`plan.steps`（P）、`confidence`（V_pre）  
- **PluginCommand**：纯 A，无成败判定、无下一跳  
- **PluginResult**：`verification.evidence`（V），必填结构化证据  
- **routes.yaml**：`when` 读 verification；**R** 求值顺序见 [路由规范](../specs/routing-intent.md)  

完整 JSON 示例见 [OpenHarness 协议 §3–4](../specs/openharness-protocol.md)。

### 8.6 Turn 状态机

```
pending → brain_done → (plan 空 → completed)
              │
              ▼ dispatch A
         plugin_running → plugin_done → R 求值 → completed | partial | failed
```

### 8.7 验收代理

| 模式 | 行为 |
|------|------|
| `self_report` | MVP：status=success 即 V.passed |
| `brain_verify` | 插件返 evidence → Brain 二次判 target.success_criteria |
| `rule_verify` | Engine 按 routes 表达式读 evidence |

---

## 9. Harness 治理

**Harness** 不是模块名，而是 **Engine + 契约 + 插件协议** 共同承担的约束：

- 智能从哪来（大脑引擎）  
- 能做什么（工具网关、插件白名单）  
- 如何验收（PluginResult、验收代理）  
- 如何审计（trace_id、结构化日志）  

**禁止 Agent 裸奔**：Shell 不得无契约、无审计地直连 Brain 或插件。

### 9.1 运行闭环四件套

| # | 名称 | 落点 | Phase |
|---|------|------|-------|
| 1 | 验收代理 | 读 V 判 T | 2+ |
| 2 | 工具网关 | Dispatcher 白名单 + schema + audit | 1 |
| 3 | Teardown | Turn 结束更新 Session | 1 |
| 4 | Compaction | recent_turns 窗口 / 摘要 | 3 |

### 9.2 五种协作模式（评审用语）

| 模式 | 落点 |
|------|------|
| 路由 Routing | Engine Router + intent |
| 提示链 Prompt Chaining | Brain 多步 plan |
| 并行 Parallelization | 多 Shell 实例 |
| 编排-执行 Orchestrator-Workers | Engine 薄编排；业务在插件 |
| 评估-优化 Evaluator-Optimiser | 契约测试 + schema + QA |

### 9.3 Agent 五要素（设计模板）

新建 Shell、插件或 Brain 服务时填齐：**Role · Goal · Tools · Rules · Output Format**（对应 manifest、intent、白名单、四层红线、JSON Schema）。

### 9.4 Shell 红线

1. Shell **只**采集与呈现  
2. Engine 为 Session / 路由 / Trace **唯一真源**  
3. IM 内置 LLM **不**作为默认 Brain 路径  
4. 内置控制台 UI **不是** OSS 默认交付物  

---

## 10. 系统边界

### In Scope（开源核心）

- OpenHarness Shell ↔ Engine  
- BrainRequest / BrainResponse、PluginCommand / PluginResult  
- Session / Turn、`routes.yaml`、trace、插件加载  
- `schemas/` 契约与契约测试  

### Out of Scope（有意不做）

- 内置 LLM 路由中枢、SOP 执行图引擎、RPA 子系统  
- 内置 Web 控制台、数字人、RBAC / 多租户 / 计费  
- 强制 K8s、消息队列、向量库  

---

## 11. 反模式（评审一票否决）

| 征兆 | 违反 | 修法 |
|------|------|------|
| Brain 内写库 | Brain 做 A | 移到插件 |
| 插件内解析用户原话 | 插件做 T | 移到 Brain |
| 插件内 dispatch 下一插件 | V 吞 R | 只返 verification |
| Engine 内 VIP 分支 | Engine 做 T | 移到 intent / routes |
| routes 写脚本 | R 非数据 | when 表达式 |
| PluginResult 只有 ok:true | 无 V 证据 | 必填 verification.evidence |

---

## 12. 评审 5 问（强制）

合入新 Turn 流程 / 插件 / 路由 / Brain prompt 前：

1. **T 是什么**？success_criteria？  
2. **P 是什么**？plan 或 routes 可列？  
3. **A 在哪些节点**？command 单一职责？  
4. **V 怎么读**？evidence 结构化？  
5. **R 怎么选**？routes 数据声明还是代码？  

**任意一问答不上来 → 重新设计。**

---

## 13. 成功标准

1. 换飞书 / TG **只改 Shell 插件**，Brain 与业务插件不动  
2. 换模型 **只改** `brain.yaml`  
3. 契约可测（JSON Schema + OH 金样）  
4. 二次开发者读本文 + STRUCTURE 即可扩展，无需改 Engine 核心  

---

## 14. 关联文档

| 文档 | 内容 |
|------|------|
| [OpenHarness 协议](../specs/openharness-protocol.md) | Shell↔Engine + Brain/Plugin 契约 |
| [路由（R）](../specs/routing-intent.md) | routes.yaml |
| [会话与状态](../specs/session-state.md) | Session / Turn |
| [扩展点](../extension/extension-points.md) | 插件模型 |
| [插件 TPAVR（L1）](../extension/plugin-tpavr-guide.md) | handler 内五元素 |
| [STRUCTURE.md](../../STRUCTURE.md) | 代码目录 |
| [路线图](../roadmap/phase-plan.md) | 分阶段交付 |
