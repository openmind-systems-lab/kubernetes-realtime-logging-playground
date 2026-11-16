#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
docker build -t omsl/logging-demo:v1 -f apps/Dockerfile apps/
kind load docker-image omsl/logging-demo:v1 --name kubetail-lab
