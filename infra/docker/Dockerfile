# syntax=docker/dockerfile:1.7

# ---- Stage 1: build wheels ---------------------------------------------------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /wheels
COPY requirements/base.txt /wheels/base.txt
RUN pip wheel --wheel-dir=/wheels -r /wheels/base.txt


# ---- Stage 2: runtime --------------------------------------------------------
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings.prod \
    APP_HOME=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl tini \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash app

WORKDIR ${APP_HOME}

COPY --from=builder /wheels /wheels
COPY requirements/base.txt /tmp/base.txt
RUN pip install --no-index --find-links=/wheels -r /tmp/base.txt \
    && rm -rf /wheels /tmp/base.txt

COPY --chown=app:app . ${APP_HOME}/

RUN chmod +x scripts/entrypoint.sh

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/v1/drf/health/ || exit 1

ENTRYPOINT ["/usr/bin/tini", "--", "scripts/entrypoint.sh"]
CMD ["gunicorn", "CacheLayerBlog.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-"]
