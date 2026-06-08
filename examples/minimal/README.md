# examples/minimal/

5 分钟跑通 Thin Engine。

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

## Docker

```bash
docker compose -f examples/minimal/docker-compose.yml up --build
```

可选 HTTP Brain sidecar：

```bash
docker compose -f examples/minimal/docker-compose.yml --profile http-brain up --build
```
