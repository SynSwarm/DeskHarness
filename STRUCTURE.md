# DeskHarness – 代码目录结构总览

> 配合 `README.md`、`doc/architecture/architecture.md` 一起阅读。

```text
DeskHarness/
├── cmd/                       # Go 风格 launcher（`python cmd/deskharness/main.py`）
│   └── deskharness/
│
├── app/                       # 【应用编排层】API + 用例 + DTO
│   ├── cli.py                 # `deskharness serve` · `plugin new`
│   ├── factory.py             # FastAPI 装配
│   ├── plugin_scaffold.py     # 插件脚手架模板
│   ├── api/
│   │   ├── openharness.py     # GET /health · POST /invoke
│   │   └── shells.py          # POST /shells/webhook-generic/inbound
│   ├── services/              # invoke、runtime、brain_factory
│   └── schemas/               # OH / Brain / Plugin / manifest DTO
│
├── core/                      # 【Engine 心脏】Thin 子集
│   ├── engine.py              # Turn 调度
│   ├── session_store.py       # SQLite Session
│   ├── router.py              # routes.yaml（R）
│   ├── dispatcher.py          # PluginCommand 网关
│   ├── plugin_loader.py       # manifest 发现与 handler 加载
│   ├── brain_client.py        # mock / http Brain
│   ├── brain_prompt_template.py  # prompt-template Brain
│   └── runtime/               # 验收代理、compaction 占位
│
├── configs/
│   ├── config.template.yaml
│   ├── routes.yaml
│   ├── brain.yaml
│   └── brain.prompt-template.yaml
│
├── pkg/                       # 公开 SDK（插件唯一依赖）
│   └── plugin/                # HandlerContext · ShellAdapter
│
├── plugins/                   # 扁平；plugin_type: shell | plugin
│   ├── webhook-generic/       # Shell（adapter.py）
│   ├── feishu-bot/            # Shell 占位
│   ├── noop/ · echo/          # 业务插件（handler.py）
│   └── order-lookup/          # sync-http 占位（Phase 3）
│
├── memory/sessions/ · memory/logs/
├── schemas/                   # JSON Schema + OH 金样
├── examples/minimal/          # Dockerfile · docker-compose.yml
├── tests/
│   ├── contract/openharness/
│   └── integration/
├── doc/
├── PROGRESS.md
└── STRUCTURE.md
```

---

## 依赖方向

```text
cmd/          → app/ → core/
app/          → core/、memory/
plugins/*     → pkg/ ONLY
core/         → memory/、configs/
禁止：plugins/ → app/ / core/ 私有实现
```

---

## 插件约定

- 目录 **`plugins/<plugin_id>/`** 扁平；`manifest.yaml` + `handler.py`（plugin）或 `adapter.py`（shell）。
- 脚手架：`deskharness plugin new <id> --type plugin|shell`

---

## 新增功能落点

| 需求 | 落点 |
|------|------|
| OH invoke | `app/api/openharness.py` |
| Session / Turn | `core/engine.py`、`core/session_store.py` |
| 路由 R | `core/router.py`、`configs/routes.yaml` |
| 插件加载 | `core/plugin_loader.py` |
| Shell 入站 | `app/api/shells.py`、`plugins/<shell-id>/adapter.py` |
| Brain 适配 | `core/brain_client.py`、`core/brain_prompt_template.py` |

---

## 关联文档

- [架构](./doc/architecture/architecture.md)
- [扩展点](./doc/extension/extension-points.md)
- [进度](./PROGRESS.md)
