#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
kubectl apply -f "$ROOT/k8s/apps.yaml"
for app in orders-api payments-api background-worker; do
  kubectl rollout status "deployment/$app" -n logging-demo --timeout=120s
done
kubectl get pods -n logging-demo -o wide
