#!/usr/bin/env bash
set -euo pipefail

Region="us-east-1"
StackEcr="cinehub-ecr"
ImageName="cinehub"
ImageTag="latest"
Dockerfile="Dockerfile.acoplada"
ContextDir="."
EcrUriOverride=""

echo "==> REGION:      $Region"
echo "==> STACK_ECR:   $StackEcr"
echo "==> IMAGE_NAME:  $ImageName"
echo "==> IMAGE_TAG:   $ImageTag"
echo "==> DOCKERFILE:  $Dockerfile"
echo "==> CONTEXT_DIR: $ContextDir"

AccountId=$(aws sts get-caller-identity --query Account --output text --region "$Region")
BaseEcr="${AccountId}.dkr.ecr.${Region}.amazonaws.com"

if [ -n "$EcrUriOverride" ]; then
  RepoUri="$EcrUriOverride"
else
  RepoUri=$(aws cloudformation describe-stacks \
    --stack-name "$StackEcr" --region "$Region" \
    --query "Stacks[0].Outputs[?OutputKey=='RepositoryUri'].OutputValue" \
    --output text)
fi

if [ -z "$RepoUri" ] || [ "$RepoUri" = "None" ]; then
  echo "No pude obtener RepositoryUri. Revisa el stack $StackEcr u ofrece -EcrUriOverride" >&2
  exit 1
fi

echo "==> ACCOUNT_ID:  $AccountId"
echo "==> ECR BASE:    $BaseEcr"
echo "==> REPO_URI:    $RepoUri"

aws ecr get-login-password --region "$Region" | docker login --username AWS --password-stdin "$BaseEcr" >/dev/null

docker build -f "$Dockerfile" -t "${ImageName}:${ImageTag}" "$ContextDir"
docker tag "${ImageName}:${ImageTag}" "${RepoUri}:${ImageTag}"
docker push "${RepoUri}:${ImageTag}"

echo "✅ Push completado."
