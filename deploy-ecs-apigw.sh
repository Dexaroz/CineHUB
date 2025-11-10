#!/usr/bin/env bash
set -euo pipefail

# ===== Config =====
STACK_NAME="${STACK_NAME:-cinehub-ecs-apigw}"
REGION="${AWS_REGION:-us-east-1}"
TEMPLATE_FILE="${TEMPLATE_FILE:-cloudformation/ecs-apigw.yaml}"

IMAGE_NAME="${IMAGE_NAME:-movie-app:latest}"
VPC_ID="${VPC_ID:-vpc-04f4b0340cb9910ee}"
VPC_CIDR="${VPC_CIDR:-172.31.0.0/16}"
DB_DDB_NAME="${DB_DDB_NAME:-movies}"

echo "==> Región:        ${REGION}"
echo "==> Stack:         ${STACK_NAME}"
echo "==> Template:      ${TEMPLATE_FILE}"
echo "==> ImageName:     ${IMAGE_NAME}"
echo "==> VpcId:         ${VPC_ID}"
echo "==> VpcCidr:       ${VPC_CIDR}"
echo "==> DBDynamoName:  ${DB_DDB_NAME}"

# ===== Validar requisitos =====
command -v aws >/dev/null 2>&1 || { echo "Falta AWS CLI v2 en PATH"; exit 1; }

# ===== Validar plantilla =====
aws cloudformation validate-template --template-body "file://${TEMPLATE_FILE}" >/dev/null

# ===== Descubrir 2 subnets del VPC (en AZs distintas si es posible) =====
echo "Descubriendo subnets en ${VPC_ID}…"
SUBNET_IDS=$(aws ec2 describe-subnets \
  --region "${REGION}" \
  --filters "Name=vpc-id,Values=${VPC_ID}" \
  --query "sort_by(Subnets,&AvailabilityZone)[].SubnetId" \
  --output text)

read -r S1 S2 _ <<< "${SUBNET_IDS:-}"
if [[ -z "${S1:-}" || -z "${S2:-}" ]]; then
  echo "No se encontraron al menos 2 subnets en ${VPC_ID}" >&2
  exit 1
fi
SUBNETS_CSV="${S1},${S2}"
echo "==> SubnetIds:     ${SUBNETS_CSV}"

# ===== Desplegar =====
echo "Desplegando stack…"
aws cloudformation deploy \
  --stack-name "${STACK_NAME}" \
  --template-file "${TEMPLATE_FILE}" \
  --parameter-overrides \
      ImageName="${IMAGE_NAME}" \
      VpcId="${VPC_ID}" \
      VpcCidr="${VPC_CIDR}" \
      SubnetIds="${SUBNETS_CSV}" \
      DBDynamoName="${DB_DDB_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset \
  --region "${REGION}"

echo "Esperando finalización…"
aws cloudformation wait stack-create-complete --stack-name "${STACK_NAME}" --region "${REGION}" \
  || aws cloudformation wait stack-update-complete --stack-name "${STACK_NAME}" --region "${REGION}" || true

# ===== Outputs útiles =====
echo "=== Outputs del stack ==="
aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" --region "${REGION}" \
  --query "Stacks[0].Outputs" --output table

API_URL=$(aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" --region "${REGION}" \
  --query "Stacks[0].Outputs[?OutputKey=='APIEndpoint'].OutputValue" --output text)

echo "=== Endpoint de la API ==="
echo "${API_URL}"
