# feishu-bot Shell

飞书外延 Shell — **Phase 4 计划**（v0.1.0：manifest 占位，尚未实现）。

## 当前替代

多渠道验证请使用已交付的 [`webhook-generic`](../webhook-generic/README.md) Shell，或直接调用 OpenHarness `POST /openharness/invoke`。

## 实现要点（规划）

- `to_invoke_request(raw)` / `from_invoke_response(resp)` — OpenHarness 转换
- **禁止**直连 Brain 或插件；Session 真源在 Engine

见 `doc/extension/extension-points.md` §2 · [`doc/roadmap/phase-plan.md`](../../doc/roadmap/phase-plan.md) Phase 4。
