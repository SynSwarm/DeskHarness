# core/

Engine 心脏（Thin 子集）。

| 模块 | 职责 |
|------|------|
| `engine.py` | Turn 编排 + context compaction |
| `session_store.py` | SQLite Session |
| `session/redis_store.py` | Redis Session（可选 `[redis]`） |
| `session/factory.py` | Session 后端选择 |
| `router.py` | `routes.yaml`（R 层）+ dry-run |
| `dispatcher.py` | local-script · sync-http · async-webhook |
| `plugin_loader.py` | manifest 发现 |
| `plugin_sandbox.py` | handler 超时 / subprocess 沙箱 |
| `plugin_subprocess.py` | 沙箱子进程入口 |
| `async_tasks.py` | async-webhook 回调任务表 |
| `brain_client.py` | mock / HTTP Brain |
| `brain_prompt_template.py` | 规则模板 Brain |
| `structured_log.py` | JSONL turn 日志 |
| `metrics.py` | 进程内计数器 |
| `rate_limit.py` | 令牌桶限流 |
| `runtime/compaction.py` | 长会话上下文压缩 |
