#!/usr/bin/env bash
set -euo pipefail
PORT="${LOCAL_PORT:-18081}"
kubectl port-forward -n logging-demo svc/orders-api "$PORT:8080" >/tmp/kubetail-orders-port-forward.log 2>&1 &
PF_PID=$!
cleanup(){ kill "$PF_PID" 2>/dev/null || true; }
trap cleanup EXIT
for _ in $(seq 1 30); do
  curl -fsS "http://127.0.0.1:$PORT/health" >/dev/null 2>&1 && break
  sleep 1
done
for i in $(seq 1 10); do
  CID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
  echo "Sending order $i (correlation_id=$CID)"
  curl -fsS -X POST "http://127.0.0.1:$PORT/orders" \
    -H 'Content-Type: application/json' -H "X-Correlation-ID: $CID" \
    -d "{\"item\":\"demo-item-$i\",\"quantity\":$((i % 3 + 1))}"
  echo
  sleep 1
done
