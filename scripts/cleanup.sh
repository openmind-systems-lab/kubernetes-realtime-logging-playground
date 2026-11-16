#!/usr/bin/env bash
set -euo pipefail
kubectl delete namespace logging-demo --ignore-not-found
helm uninstall kubetail -n kubetail --ignore-not-found 2>/dev/null || true
kubectl delete namespace kubetail --ignore-not-found
echo "Resources removed. Kind cluster remains; delete it with: kind delete cluster --name kubetail-lab"
