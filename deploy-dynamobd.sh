#!/usr/bin/env bash
set -euo pipefail

# === Configuración ===
STACK_NAME="${STACK_NAME:-cinehub-ddb}"
REGION="${AWS_REGION:-us-east-1}"
TEMPLATE_FILE="${TEMPLATE_FILE:-cloudformation/db.yaml}"

TABLE_NAME_PARAM="${TABLE_NAME:-movies}"

echo "Validando plantilla: ${TEMPLATE_FILE}"
aws cloudformation validate-template \
  --template-body "file://${TEMPLATE_FILE}" >/dev/null

echo "Desplegando stack: ${STACK_NAME} en ${REGION}"
aws cloudformation deploy \
  --stack-name "${STACK_NAME}" \
  --template-file "${TEMPLATE_FILE}" \
  --parameter-overrides TableName="${TABLE_NAME_PARAM}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset \
  --region "${REGION}"

echo "Esperando a que el stack esté completo…"
aws cloudformation wait stack-create-complete --stack-name "${STACK_NAME}" --region "${REGION}" \
  || aws cloudformation wait stack-update-complete --stack-name "${STACK_NAME}" --region "${REGION}" || true

echo "=== Outputs del stack ==="
aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" --region "${REGION}" \
  --query "Stacks[0].Outputs" --output table

TABLE_NAME=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" --region "${REGION}" \
  --query "Stacks[0].Outputs[?OutputKey=='TableName'].OutputValue" --output text)

echo "=== Estado real de la tabla en DynamoDB (${TABLE_NAME}) ==="
aws dynamodb describe-table --table-name "${TABLE_NAME}" --region "${REGION}" \
  --query "Table.{TableName:TableName,Status:TableStatus,ItemCount:ItemCount,ARN:TableArn,BillingMode:BillingModeSummary.BillingMode}" \
  --output table

echo "Despliegue terminado."
