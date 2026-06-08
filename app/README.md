# app/

应用编排层：HTTP API、用例服务、运行时 DTO、CLI。

| 模块 | 职责 |
|------|------|
| `cli.py` | `deskharness serve` · `plugin new` |
| `factory.py` | FastAPI 装配 |
| `plugin_scaffold.py` | 插件 / Shell 脚手架 |
| `api/openharness.py` | `/openharness/health`、`/invoke` |
| `api/shells.py` | `/shells/webhook-generic/inbound` |
| `services/` | invoke、runtime、brain_factory |
| `schemas/` | OH / Brain / Plugin / manifest DTO |

JSON Schema 真源在仓库根 `schemas/`。
