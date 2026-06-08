# 会话与状态

**Engine** 是 Session **唯一真源**；持久化落 **`memory/sessions/`**（`app/services/session` + `core/engine` 读写）。

---

## 1. 原则

| 原则 | 说明 |
|------|------|
| 大脑引擎无状态 | context 由 Engine 组装 |
| 插件无会话 | 单次 PluginCommand |
| Shell 无业务态 | 仅 UI 缓存 |

---

## 2. Session 结构

```yaml
session:
  session_id: "sess_01HXYZ..."
  subject:
    channel_user_id: "feishu:ou_xxx"
    display_name: "张三"
  shell_id: "feishu-bot"
  context:
    recent_turns: []
    session_vars: {}
```

---

## 3. 生命周期

Shell 经 **OpenHarness invoke** 进入 Engine → 按 `channel_user_id` resolve/create `session_id`。

---

## 4. Context 组装

Engine 调大脑引擎前注入 `recent_turns`、`session_vars`；剥离 Shell 渠道 metadata（`shell_meta` 等）。

---

## 5. session_vars

插件 manifest `exports` 从 `verification.evidence` 写入 session_vars。

---

## 6. 配置

`configs/config.yaml` — KV 后端、TTL（`engine:` 段；旧名 `engine.yaml` / `gateway.yaml` 仅兼容）。
