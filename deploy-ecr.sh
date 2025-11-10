#!/usr/bin/env bash
set -euo pipefail

STACK_NAME="${STACK_NAME:-cinehub-ecr}"
REGION="${AWS_REGION:-us-east-1}"
TEMPLATE_FILE="${TEMPLATE_FILE:-cloudformation/ecr.yaml}"
REPO_NAME="${REPOSITORY_NAME:-movie-app}"

echo "Validando plantilla: ${TEMPLATE_FILE}"
aws cloudformation validate-template \
  --template-body "file://${TEMPLATE_FILE}" >/dev/null

echo "Desplegando stack: ${STACK_NAME} en ${REGION}"
aws cloudformation deploy \
  --stack-name "${STACK_NAME}" \
  --template-file "${TEMPLATE_FILE}" \
  --parameter-overrides RepositoryName="${REPO_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --no-fail-on-empty-changeset \
  --region "${REGION}"

echo "Esperando finalización del stack…"
aws cloudformation wait stack-create-complete --stack-name "${STACK_NAME}" --region "${REGION}" \
  || aws cloudformation wait stack-update-complete --stack-name "${STACK_NAME}" --region "${REGION}" || true

echo "=== Outputs del stack ==="
aws cloudformation describe-stacks \
  --stack-name "${STACK_NAME}" --region "${REGION}" \
  --query "Stacks[0].Outputs" --output table

echo "=== Estado del repositorio ==="
aws ecr describe-repositories \
  --repository-names "${REPO_NAME}" --region "${REGION}" \
  --query "repositories[0].{Name:repositoryName,Uri:repositoryUri,Arn:repositoryArn,ScanOnPush:imageScanningConfiguration.scanOnPush,Immutable:imageTagMutability}" \
  --output table

echo "Despliegue ECR terminado."
