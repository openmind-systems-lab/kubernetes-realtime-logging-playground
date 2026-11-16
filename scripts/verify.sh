#!/usr/bin/env bash
set -euo pipefail
kubectl get namespace logging-demo >/dev/null
for app in orders-api payments-api background-worker; do
  kubectl rollout status "deployment/$app" -n logging-demo --timeout=30s
  ready="$(kubectl get deployment "$app" -n logging-demo -o jsonpath='{.status.readyReplicas}')"
  desired="$(kubectl get deployment "$app" -n logging-demo -o jsonpath='{.spec.replicas}')"
  [[ "${ready:-0}" == "$desired" ]] || { echo "$app: ${ready:-0}/$desired ready" >&2; exit 1; }
done
echo "All application deployments are healthy."
kubectl get pods -n logging-demo
