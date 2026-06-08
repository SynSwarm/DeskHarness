# cmd/deskharness/

Python CLI 入口（ADR-004）。

```bash
pip install -e ".[dev]"
deskharness serve --config configs/config.yaml
```

Phase 1 实现：`app/factory.py` 组装 FastAPI + `app/api/openharness`。
