# core/

Engine 心脏（Thin 子集）。

| 模块 | 职责 |
|------|------|
| `engine.py` | Turn 编排：OH → Session → Brain → Plugin → outbound |
| `session_store.py` | SQLite Session 真源 |
| `router.py` | `routes.yaml`（R 层） |
| `dispatcher.py` | PluginCommand → manifest handler |
| `plugin_loader.py` | 扫描 `plugins/*/manifest.yaml` |
| `brain_client.py` | mock / HTTP Brain |
| `brain_prompt_template.py` | 规则模板 Brain（零 LLM） |
| `runtime/` | 验收代理、compaction 占位 |

不含 SOP 执行图引擎（商用 Fat 能力，见内部 `doc/private/`）。
