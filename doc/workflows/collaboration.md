# 协作工作流程

> 本文描述 DeskHarness 从需求到合入的 **端到端协作顺序**。角色条文见 `doc/roles/`。

---

## 1. 总览

```text
需求输入
   │
   ▼
┌──────────────┐     ┌─────────────────┐     ┌──────────────┐
│  Architect   │────►│ Engine Engineer │────►│ Shell/Plugin/│
│  架构评审     │     │  核心 / 联调      │     │ Brain Author │
└──────────────┘     └─────────────────┘     └──────┬───────┘
                                                     │
                    ┌─────────────────┐              │
                    │  Test Engineer  │◄─────────────┘
                    │  契约 + 冒烟     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   QA 门神       │
                    │  入库四步审查    │
                    └────────┬────────┘
                             │
                         git commit
                    （push 由用户本地执行）
```

---

## 2. 新会话开局工作流（所有角色）

**每次新对话、长时间未活动后恢复，必须先执行，再改代码：**

1. **读文档（只读）**
   - 必读：`README.md` → `doc/architecture/architecture.md` → 本角色 `doc/roles/<role>.md`
   - 防幻觉：`PROGRESS.md` — 未完成项不得说成已落地
2. **建立心智模型**
   - 用 2–3 句话总结：DeskHarness 做什么、当前 Phase、你的角色边界
   - 列出关键假设（例如某模块尚未实现）
3. **默认不重写**
   - 尊重四层边界与 OpenHarness 协议；重构须给 MVP + 迁移路径

---

## 3. 按场景的工作流

### 3.1 新功能 / 新渠道（Shell）

| 步骤 | 角色 | 动作 |
|------|------|------|
| 1 | Architect | 确认属于 Layer 1；是否需要 OpenHarness 新字段（若需要 → 协议评审） |
| 2 | Shell Author | 从 `examples/shells/` 或模板创建插件；实现 OpenHarness invoke 适配 |
| 3 | Engine Engineer | 注册 Shell、联调 Ingress/Egress |
| 4 | Test Engineer | mock 事件 → 断言 inbound 符合 OpenHarness schema |
| 5 | QA 门神 | 合入前四步审查 |

**出口标准**：换 Brain / 插件零改动；Session 由 Engine 创建，Shell 不传 session 业务态。

---

### 3.2 新业务动作（插件）

| 步骤 | 角色 | 动作 |
|------|------|------|
| 1 | Architect + Brain Integrator | 定义 intent 命名（`domain.verb`）；更新 `routes.yaml` 草案 |
| 2 | Plugin Author | 实现 handler 或 sync-http 服务；manifest 声明 commands + exports |
| 3 | Brain Integrator | Brain 输出对应 intent 与 action_plan.params |
| 4 | Engine Engineer | 路由联调；验证 session_vars exports |
| 5 | Test Engineer | PluginCommand → PluginResult 契约测试 |
| 6 | QA 门神 | 审查插件是否解析 NLU / 直连 Shell |

**出口标准**：插件只收 PluginCommand；失败返回结构化 error，不 crash Engine。

---

### 3.3 Brain 接入 / 换模型

| 步骤 | 角色 | 动作 |
|------|------|------|
| 1 | Architect | 确认 Brain 无状态；不持有 Session |
| 2 | Brain Integrator | 实现 HTTP 端点或选用内置 adapter（`openai-compatible` / `prompt-template`） |
| 3 | Engine Engineer | 配置 `brain.yaml`；timeout / retry |
| 4 | Test Engineer | 固定 BrainRequest fixture → 断言 BrainResponse schema |
| 5 | QA 门神 | 审查 Brain 内是否有插件/DB 直连 |

---

### 3.4 协议 / 架构变更（Breaking）

| 步骤 | 角色 | 动作 |
|------|------|------|
| 1 | Architect | 写 ADR：`doc/adr/NNN-title.md`（决策 / 备选 / 风险 / 回滚） |
| 2 | Architect | 更新 `doc/specs/` + bump schema 版本 |
| 3 | Engine Engineer | Engine adapter 层做版本转换（若需兼容旧客户端） |
| 4 | 各 Author | 同步插件 manifest `api_version` |
| 5 | Test Engineer | 契约测试覆盖新旧版本 |
| 6 | QA 门神 | 确认 PROGRESS / 文档 / schema 三者一致 |

---

### 3.5 准备提交 Git（QA 触发）

用户发送 **「准备提交 Git」** 或 **「Review 一下」**：

1. **QA 门神** 执行四步铁律（见 `qa-gatekeeper.md`）
2. 非 QA 角色：只输出 Commit Message 建议，**不执行** `git commit` / `git push`
3. **`git push` 仅由用户本地执行**

---

## 4. Phase 与角色投入（当前 Phase 0 → 1）

| Phase | 主责 | 协作 |
|-------|------|------|
| **0 体系冻结** | Architect | 全员读文档对齐 |
| **1 Engine MVP** | Engine Engineer | Brain Integrator 提供 mock；Test 写契约 |
| **2 插件体系** | Shell Author + Plugin Author | Engine Engineer 做 Loader |
| **3 生产就绪** | Engine Engineer + Test | Architect 审 Redis/异步插件 |
| **4 生态** | 各 Author | 官方示例 Shell/插件 |

详表见 `doc/roadmap/phase-plan.md`。

---

## 5. 协作红线（全员）

| 红线 | 说明 |
|------|------|
| 禁止跨层直连 | Shell↛Brain、Brain↛插件、插件↛Shell |
| 禁止 Engine 业务逻辑 | VIP 规则、订单逻辑在 Brain 或插件 |
| 禁止插件依赖 internal | 只依赖 `pkg/` 公开面 |
| 禁止硬编码密钥 | API Key / Token 走 env 或本地配置 |
| stub ≠ done | `PROGRESS.md` 未标 done 的不得按已落地描述 |
| 占位符禁止合入 | `// ... existing code ...` 一律打回 |

---

## 6. 文档同步义务

| 变更类型 | 必须更新 |
|----------|----------|
| 架构决策 | `doc/architecture/` + `doc/adr/` |
| 协议字段 | `doc/specs/openharness-protocol.md` + `schemas/` |
| 新插件类型 | `doc/extension/extension-points.md` |
| 任务状态 | `PROGRESS.md` |
| 角色边界变化 | `doc/roles/` + `.cursor/rules/` |
