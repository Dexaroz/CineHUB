#!/usr/bin/env bash
set -euo pipefail

########################################
# CONFIG EDITABLE
########################################
REGION="${REGION:-us-east-1}"

# Nombres de los stacks
STACK_DDB="${STACK_DDB:-cinehub-ddb}"
STACK_ECR="${STACK_ECR:-cinehub-ecr}"
STACK_ECS="${STACK_ECS:-cinehub-ecs}"
STACK_API="${STACK_API:-cinehub-apigw}"

# Archivos de plantilla (ajusta rutas si cambian)
TPL_DDB="${TPL_DDB:-db_dynamodb.yml}"
TPL_ECR="${TPL_ECR:-ecr.yml}"¡
TPL_ECS="${TPL_ECS:-ecs-fargate.yml}"¡
TPL_API="${TPL_API:-apigw-rest-vpclink.yml}"¡

# Parámetros de red existentes
VPC_ID="${VPC_ID:-vpc-xxxxxxxx}"
SUBNETS_CSV="${SUBNETS_CSV:-subnet-aaaaaaa,subnet-bbbbbbb}"

# Tabla DynamoDB
TABLE_NAME="${TABLE_NAME:-movies}"

# Repositorio/imagen
REPO_NAME="${REPO_NAME:-cinehub}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

########################################
# AUX
########################################
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

echo "===> Región:     ${REGION}"
echo "===> Cuenta:     ${ACCOUNT_ID}"
echo "===> VPC:        ${VPC_ID}"
echo "===> Subnets:    ${SUBNETS_CSV}"
echo "===> Tabla DDB:  ${TABLE_NAME}"
echo "===> Repo ECR:   ${REPO_NAME}"
echo "===> Imagen tag: ${IMAGE_TAG}"

########################################
# 1) ECR (repo)
########################################
echo "===> Desplegando ECR (${STACK_ECR})"
aws cloudformation deploy \
  --stack-name "${STACK_ECR}" \
  --template-file "${TPL_ECR}" \
  --parameter-overrides RepositoryName="${REPO_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}"

REPO_URI="$(aws cloudformation describe-stacks --stack-name "${STACK_ECR}" \
  --query "Stacks[0].Outputs[?OutputKey=='RepositoryUri'].OutputValue" --output text --region "${REGION}")"

echo "===> ECR URI: ${REPO_URI}"

########################################
# 2) Build & Push imagen
########################################
echo "===> Login en ECR"
aws ecr get-login-password --region "${REGION}" \
  | docker login --username AWS --password-stdin "${ECR_URI}"

echo "===> Build local"
docker build -t "${REPO_NAME}:${IMAGE_TAG}" .

echo "===> Tag & push"
docker tag  "${REPO_NAME}:${IMAGE_TAG}" "${REPO_URI}:${IMAGE_TAG}"
docker push "${REPO_URI}:${IMAGE_TAG}"

########################################
# 3) DynamoDB (tabla)
########################################
echo "===> Desplegando DynamoDB (${STACK_DDB})"
aws cloudformation deploy \
  --stack-name "${STACK_DDB}" \
  --template-file "${TPL_DDB}" \
  --parameter-overrides TableName="${TABLE_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}"

TABLE_ARN="$(aws cloudformation describe-stacks --stack-name "${STACK_DDB}" \
  --query "Stacks[0].Outputs[?OutputKey=='TableArn'].OutputValue" --output text --region "${REGION}")"

echo "===> DDB Table ARN: ${TABLE_ARN}"

########################################
# 4) ECS + NLB
########################################
echo "===> Desplegando ECS+NLB (${STACK_ECS})"
aws cloudformation deploy \
  --stack-name "${STACK_ECS}" \
  --template-file "${TPL_ECS}" \
  --parameter-overrides \
      VpcId="${VPC_ID}" \
      Subnets="${SUBNETS_CSV}" \
      ContainerImage="${REPO_URI}:${IMAGE_TAG}" \
      MoviesTableName="${TABLE_NAME}" \
      DynamoDbTableArn="${TABLE_ARN}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}"

NLB_ARN="$(aws cloudformation describe-stacks --stack-name "${STACK_ECS}" \
  --query "Stacks[0].Outputs[?OutputKey=='NlbArn'].OutputValue" --output text --region "${REGION}")"

NLB_DNS="$(aws cloudformation describe-stacks --stack-name "${STACK_ECS}" \
  --query "Stacks[0].Outputs[?OutputKey=='NlbDNS'].OutputValue" --output text --region "${REGION}")"

echo "===> NLB ARN: ${NLB_ARN}"
echo "===> NLB DNS: ${NLB_DNS}"

########################################
# 5) API Gateway + VPC Link
########################################
echo "===> Desplegando API GW + VPC Link (${STACK_API})"
aws cloudformation deploy \
  --stack-name "${STACK_API}" \
  --template-file "${TPL_API}" \
  --parameter-overrides \
      NlbArn="${NLB_ARN}" \
      NlbDnsName="${NLB_DNS}" \
      StageName="prod" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "${REGION}"

API_URL="$(aws cloudformation describe-stacks --stack-name "${STACK_API}" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiInvokeUrl'].OutputValue" --output text --region "${REGION}")"

echo "==================================================="
echo "✅ Despliegue completado"
echo "API URL: ${API_URL}"
echo "Health:  ${API_URL%/prod*}/prod/health"
echo "Movies:  ${API_URL%/prod*}/prod/movies"
echo "==================================================="
