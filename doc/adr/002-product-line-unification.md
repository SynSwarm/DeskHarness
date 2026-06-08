# ADR-002: 术语与协议统一

## 状态

Accepted · 2026-06-07

## 决策

- DeskHarness OSS = Thin **Engine** + OpenHarness + 插件  
- 公开架构真源：**`doc/architecture/architecture.md`**  
- 协议：Shell↔Engine 只用 **OpenHarness**（不另造 DeskEnvelope 等品牌词）  
- 术语：Shell、Engine、插件、plugin_id、PluginCommand/Result  
- 目录：`app/` + `core/` + 扁平 `plugins/` + `memory/`  

## 弃用词

DeskEnvelope、Skin、Action 层（作层名）、action_id、ActionCommand、整包 `gateway/`、`plugins/shells/`。

## 商用产品线（内部）

术语对照、升级路径、目录映射 — **`doc/private/`**（私有，不入库）。

## 仓库布局

见根目录 **`STRUCTURE.md`**。
