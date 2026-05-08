#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-http://localhost:8000}"
USERS="${USERS:-200}"
SPAWN="${SPAWN:-20}"
DURATION="${DURATION:-60s}"
OUT_DIR="${OUT_DIR:-benchmarks/reports/$(date +%Y%m%d-%H%M%S)}"

mkdir -p "${OUT_DIR}"

locust \
    --locustfile benchmarks/locust/locustfile.py \
    --host "${HOST}" \
    --users "${USERS}" \
    --spawn-rate "${SPAWN}" \
    --run-time "${DURATION}" \
    --headless \
    --csv "${OUT_DIR}/locust" \
    --html "${OUT_DIR}/locust.html"

echo "Report written to ${OUT_DIR}"
