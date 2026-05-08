#!/usr/bin/env bash
set -euo pipefail

HOST="${HOST:-http://localhost:8000}"
N="${N:-5000}"
C="${C:-50}"
OUT_DIR="${OUT_DIR:-benchmarks/reports/$(date +%Y%m%d-%H%M%S)-ab}"

mkdir -p "${OUT_DIR}"

run() {
    local rail="$1"; shift
    local path="$1"; shift
    local out="${OUT_DIR}/${rail}.txt"
    echo ">> ${rail} ${path}" | tee "${out}"
    ab -n "${N}" -c "${C}" -k "${HOST}${path}" | tee -a "${out}"
}

run drf-health   /api/v1/drf/health/
run ninja-health /api/v1/ninja/health

echo
echo "Tip: re-run after seeding + auth to compare list/detail endpoints."
