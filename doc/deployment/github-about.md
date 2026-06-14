# GitHub 仓库 About 配置

面向维护者：在 **Settings → General → About** 中配置仓库描述与 Topics。  
此页为 **真源备忘**；`pyproject.toml` 的 `[project] description` 应与英文 Description 语义一致。

用户可见入口：根目录 [README.md](../../README.md) · [README.zh-CN.md](../../README.zh-CN.md)。

---

## Description（英文，推荐）

GitHub About 默认展示英文。复制以下内容（≤350 字符）：

```text
Thin Integration Harness Engine for SMEs — decouple Shell, Brain, and plugins via OpenHarness. Headless, contract-first orchestration. Not an Agent framework.
```

### 中文参考（不写入 GitHub About，用于国内宣传）

```text
面向中小企业的开源 Thin Harness Engine。用 OpenHarness 协议解耦 Shell、Brain 与插件，无头、契约驱动，非 Agent 框架。
```

### 弃用表述（勿再使用）

| 弃用 | 原因 | 改用 |
|------|------|------|
| `AI agent gateway` | 像 Agent 框架，与定位冲突 | Integration Harness / contract layer |
| `Skin` | ADR-002 弃用词 | **Shell** |
| `Action`（作层名） | ADR-002 弃用词 | **Plugin** |
| `gateway`（泛指） | 易与 API Gateway 混淆 | **Engine** / OpenHarness endpoint |

---

## Topics（推荐 10 个）

在 **About → Topics** 中添加（顺序可按优先级）：

```text
openharness
integration-layer
headless-engine
python
harness
ai-orchestration
llm
feishu-bot
fastapi
chatbot
```

| Topic | 用途 |
|-------|------|
| `openharness` | 协议差异化，与 [SynSwarm/OpenHarness](https://github.com/SynSwarm/OpenHarness) 联动 |
| `integration-layer` | 集成编排层定位 |
| `headless-engine` | 无 UI、可嵌入 |
| `python` | 运行时 |
| `harness` | 品类词，竞争面小 |
| `ai-orchestration` | 通用发现 |
| `llm` | Brain 外置 / 大模型集成 |
| `feishu-bot` | 国内渠道楔子（Shell 实现为 Phase 4，Topic 可保留作方向） |
| `fastapi` | 技术栈，吸引 Python 后端 |
| `chatbot` | 实用搜索词 |

**不建议添加：** `langchain`、`crewai`、`agent-framework` — 易被归类为 Agent 框架竞品，而非互补层。

---

## 操作步骤

1. 打开 [SynSwarm/DeskHarness](https://github.com/SynSwarm/DeskHarness) → **Settings** → **General**
2. 滚动至 **About** → **Edit repository details**
3. **Description** — 粘贴上方英文 Description
4. **Website**（可选）— 文档站上线后填入 MkDocs URL；v0.1.0 可留空或链到架构文档：
   `https://github.com/SynSwarm/DeskHarness/blob/main/doc/architecture/architecture.md`
5. **Topics** — 添加上表 10 个 tag
6. 保存

### 与 OpenHarness 仓库互链（建议）

在 [SynSwarm/OpenHarness](https://github.com/SynSwarm/OpenHarness) 的 README **Implementations** 段链到本仓；本仓 README 已链回 OpenHarness 协议仓库。

---

## 发布前检查

纳入 [版本发布清单](./release.md)：

- [ ] Description 已更新，无 Skin / Action / agent gateway
- [ ] Topics 已添加（至少 `openharness`、`integration-layer`、`python`）
- [ ] `pyproject.toml` `[project] description` 与 About 语义一致
- [ ] README 首段 Slogan 与 About 不矛盾（「换飞书」为 Phase 4 愿景，示例表已标注交付状态）

---

## 相关

- [版本发布](./release.md)
- [Docker 部署](./docker.md)
- [ADR-002 术语统一](../adr/002-product-line-unification.md)
- [CHANGELOG.md](../../CHANGELOG.md)
