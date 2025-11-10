#!/usr/bin/env bash
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-east-1}"
DB_TEMPLATE="${DB_TEMPLATE:-cloudformation/db.yaml}"
ECR_TEMPLATE="${ECR_TEMPLATE:-cloudformation/ecr.yaml}"
ECS_TEMPLATE="${ECS_TEMPLATE:-cloudformation/ecs-apigw.yaml}"

STACK_DDB="${STACK_DDB:-cinehub-ddb}"
STACK_ECR="${STACK_ECR:-cinehub-ecr}"
STACK_ECS="${STACK_ECS:-cinehub-ecs-apigw}"  # <— corregido

TABLE_NAME="${TABLE_NAME:-movies}"
REPOSITORY_NAME="${REPOSITORY_NAME:-movie-app}"
IMAGE_NAME="${IMAGE_NAME:-cinehub}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DOCKERFILE="${DOCKERFILE:-Dockerfile}"
CONTEXT_DIR="${CONTEXT_DIR:-.}"

need(){ command -v "$1" >/dev/null 2>&1 || { echo "Falta comando: $1" >&2; exit 1; }; }
need aws; need docker

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Usa TUS nombres reales
DDB_SH="${SCRIPT_DIR}/deploy-dynamobd.sh"     # <— tu archivo existe con este nombre
ECR_SH="${SCRIPT_DIR}/deploy-ecr.sh"
PUSH_SH="${SCRIPT_DIR}/build-images-ecr.sh"   # <— tu archivo existe con este nombre
ECS_SH="${SCRIPT_DIR}/deploy-ecs-apigw.sh"    # <— NO existe (créalo con el contenido que te pasé)

for f in "$DDB_SH" "$ECR_SH" "$PUSH_SH"; do
  [[ -f "$f" ]] || { echo "No encuentro: $f" >&2; exit 1; }
done
if [[ ! -f "$ECS_SH" ]]; then
  echo "No encuentro: $ECS_SH"
  echo "Crea este script (deploy-ecs-apigw.sh) con el .sh que te pasé para ECS+API GW y vuelve a ejecutar."
  exit 1
fi

echo "==> Región: ${AWS_REGION}"
echo "==> Stacks: DDB=${STACK_DDB}  ECR=${STACK_ECR}  ECS=${STACK_ECS}"
echo "==> Tabla:  ${TABLE_NAME}  RepoECR: ${REPOSITORY_NAME}  Imagen: ${IMAGE_NAME}:${IMAGE_TAG}"
echo

echo ">>> [1/4] DynamoDB"
STACK_NAME="${STACK_DDB}" AWS_REGION="${AWS_REGION}" TEMPLATE_FILE="${DB_TEMPLATE}" TABLE_NAME="${TABLE_NAME}" \
bash "$DDB_SH"
echo

echo ">>> [2/4] ECR"
STACK_NAME="${STACK_ECR}" AWS_REGION="${AWS_REGION}" TEMPLATE_FILE="${ECR_TEMPLATE}" REPOSITORY_NAME="${REPOSITORY_NAME}" \
bash "$ECR_SH"
echo

echo ">>> [3/4] Build & Push imagen"
AWS_REGION="${AWS_REGION}" STACK_ECR="${STACK_ECR}" ImageName="${IMAGE_NAME}" ImageTag="${IMAGE_TAG}" Dockerfile="${DOCKERFILE}" ContextDir="${CONTEXT_DIR}" \
bash "$PUSH_SH"
echo

echo ">>> [4/4] ECS + API Gateway"
STACK_NAME="${STACK_ECS}" AWS_REGION="${AWS_REGION}" TEMPLATE_FILE="${ECS_TEMPLATE}" IMAGE_NAME="${REPOSITORY_NAME}:${IMAGE_TAG}" DB_DDB_NAME="${TABLE_NAME}" \
bash "$ECS_SH"
echo

echo ">>> Obteniendo URL y API Key…"
API_URL=$(aws cloudformation describe-stacks --stack-name "${STACK_ECS}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='APIEndpoint'].OutputValue" --output text)
API_KEY_ID=$(aws cloudformation describe-stacks --stack-name "${STACK_ECS}" --region "${AWS_REGION}" --query "Stacks[0].Outputs[?OutputKey=='APIKeyId'].OutputValue" --output text)
API_KEY_VALUE=$(aws apigateway get-api-key --api-key "${API_KEY_ID}" --include-value --region "${AWS_REGION}" --query "value" --output text)

echo
echo "==================== RESULTADO ===================="
echo "API URL  : ${API_URL}"
echo "API KEYID: ${API_KEY_ID}"
echo "API KEY  : ${API_KEY_VALUE}"
echo "==================================================="
