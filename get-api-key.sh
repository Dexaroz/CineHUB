#!/usr/bin/env bash
set -euo pipefail

# === Parámetro ===
API_KEY_ID="${1:-}"

if [[ -z "$API_KEY_ID" ]]; then
  echo "Uso: $0 <ApiKeyID>"
  exit 1
fi

# === Ejecutar comando ===
aws apigateway get-api-key \
  --api-key "$API_KEY_ID" \
  --include-value
