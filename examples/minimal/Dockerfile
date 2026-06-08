# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml README.md LICENSE ./
COPY app ./app
COPY core ./core
COPY cmd ./cmd
COPY pkg ./pkg
COPY configs ./configs
COPY plugins ./plugins
COPY schemas ./schemas
COPY examples ./examples
COPY memory ./memory

RUN pip install --no-cache-dir -e .

EXPOSE 8080

CMD ["deskharness", "serve", "--host", "0.0.0.0", "--port", "8080", "--config", "configs/config.template.yaml"]
