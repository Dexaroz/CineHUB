#!/usr/bin/env bash
set -euo pipefail

# ===== Config =====
STACK_NAME="${STACK_NAME:-cinehub-lambda-apigw}"
REGION="${AWS_REGION:-us-east-1}"
TEMPLATE_FILE="${TEMPLATE_FILE:-cloudformation/lambda-apigw.yaml}"
DDB_TABLE_NAME="${DDB_TABLE_NAME:-movies}"

echo "==> Región:        ${REGION}"
echo "==> Stack:         ${STACK_NAME}"
echo "==> Template:      ${TEMPLATE_FILE}"
echo "==> DDBTableName:  ${DDB_TABLE_NAME}"

# ===== Requisitos =====
command -v aws >/dev/null 2>&1 || { echo "Falta AWS CLI v2 en PATH"; exit 1; }

# ===== Validar plantilla =====
aws cloudformation validate-template --region "${REGION}" \
  --template-body "file://${TEMPLATE_FILE}" >/dev/null

# ===== Desplegar =====
echo "Desplegando stack…"
aws cloudformation deploy \
  --region "${REGION}" \
  --stack-name "${STACK_NAME}" \
  --template-file "${TEMPLATE_FILE}" \
  --parameter-overrides DDBTableName="${DDB_TABLE_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset

# ===== Esperar a que termine =====
aws cloudformation wait stack-create-complete --region "${REGION}" --stack-name "${STACK_NAME}" \
  || aws cloudformation wait stack-update-complete --region "${REGION}" --stack-name "${STACK_NAME}" || true

# ===== Outputs =====
echo "=== Outputs del stack ==="
aws cloudformation describe-stacks \
  --region "${REGION}" --stack-name "${STACK_NAME}" \
  --query "Stacks[0].Outputs" --output table

API_BASE_URL=$(aws cloudformation describe-stacks \
  --region "${REGION}" --stack-name "${STACK_NAME}" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiBaseUrl'].OutputValue" --output text)

MOVIES_URL=$(aws cloudformation describe-stacks \
  --region "${REGION}" --stack-name "${STACK_NAME}" \
  --query "Stacks[0].Outputs[?OutputKey=='MoviesUrl'].OutputValue" --output text)

API_KEY_ID=$(aws cloudformation describe-stacks \
  --region "${REGION}" --stack-name "${STACK_NAME}" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiKeyId'].OutputValue" --output text)

API_KEY_VALUE=$(aws apigateway get-api-key \
  --region "${REGION}" \
  --api-key "${API_KEY_ID}" \
  --include-value \
  --query 'value' --output text 2>/dev/null || echo "<no disponible>")

echo "=== Endpoint base ==="
echo "${API_BASE_URL}"
echo "=== Endpoint /movies ==="
echo "${MOVIES_URL}"
echo "=== API Key (valor) ==="
echo "${API_KEY_VALUE}"
