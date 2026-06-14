# examples/minimal/

5 分钟跑通 Thin Engine（**v0.1.0** 发布验证入口）。

## 本地

```bash
pip install -e ".[dev]"
cp configs/config.template.yaml configs/config.yaml   # 可选
deskharness serve
```

**OpenHarness 直连**

```bash
curl -s -X POST localhost:8080/openharness/invoke \
  -H 'Content-Type: application/json' \
  -d @schemas/openharness/fixtures/minimal-request.json
```

**Webhook Shell**

```bash
curl -s -X POST localhost:8080/shells/webhook-generic/inbound \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hello from webhook","session_id":"sess_demo"}'
```

**prompt-template Brain**（零 LLM，规则 YAML）

`configs/config.yaml`：

```yaml
brain:
  adapter: prompt-template
  template_file: ./configs/brain.prompt-template.yaml
```

**HTTP mock Brain**

```bash
python examples/minimal/mock_brain_server.py
# brain.adapter: http
```

**sync-http order-lookup**

```bash
python examples/minimal/mock_order_lookup_server.py
# 另开终端 deskharness serve，然后：
curl -s -X POST localhost:8080/openharness/invoke \
  -H 'Content-Type: application/json' \
  -d '{"protocol_version":"1.0.0","request_id":"req_order","request":{"context":{"session_id":"sess_o1","user_intent":"query order 12345"}}}'
```

**async-webhook async-demo**

```bash
python examples/minimal/mock_async_webhook_server.py
# routing.allowed_plugins 加入 async-demo 后，Brain 路由到 submit 命令
curl -s localhost:8080/plugins/callbacks/<task_id>
```

**Rate limit**（`configs/config.yaml`）

```yaml
engine:
  rate_limit:
    enabled: true
    requests_per_minute: 60
```

**Debug / Metrics**（`dev_mode: true`）

```bash
curl -s localhost:8080/debug/routes
curl -s localhost:8080/metrics
tail -f memory/logs/turns.jsonl
```

## Docker

**本地 build**

```bash
docker compose -f examples/minimal/docker-compose.yml up --build
```

**官方镜像**（需已发布到 GHCR）

```bash
docker compose -f examples/minimal/docker-compose.image.yml up -d
# DESKHARNESS_TAG=0.1.0 docker compose -f examples/minimal/docker-compose.image.yml up -d
```

详见 [`doc/deployment/docker.md`](../../doc/deployment/docker.md) · 发布见 [`doc/deployment/release.md`](../../doc/deployment/release.md)。

可选 HTTP Brain sidecar：

```bash
docker compose -f examples/minimal/docker-compose.yml --profile http-brain up --build
```
