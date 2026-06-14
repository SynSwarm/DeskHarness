# syntax=docker/dockerfile:1
# Official DeskHarness Engine image — see doc/deployment/docker.md

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN groupadd --gid 1000 deskharness \
 && useradd --uid 1000 --gid deskharness --shell /bin/bash --create-home deskharness

COPY pyproject.toml README.md LICENSE ./
COPY app ./app
COPY core ./core
COPY pkg ./pkg
COPY configs ./configs
COPY plugins ./plugins
COPY schemas ./schemas

RUN pip install --no-cache-dir . \
 && mkdir -p memory/sessions memory/logs \
 && chown -R deskharness:deskharness /app

USER deskharness

EXPOSE 8080

HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/openharness/health')"

CMD ["deskharness", "serve", "--host", "0.0.0.0", "--port", "8080", "--config", "configs/config.docker.yaml"]
