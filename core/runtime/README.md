# core/runtime/

运行治理：长会话压缩、后续验收代理等。

| 模块 | 职责 |
|------|------|
| `compaction.py` | Turn 前折叠旧轮次 → `session_vars._context_summary` |

配置：`engine.context.max_turns` · `keep_recent`（见 `configs/config.template.yaml`）。
