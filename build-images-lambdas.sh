#!/usr/bin/env bash
set -euo pipefail

# ===== Config =====
Region="${Region:-us-east-1}"
StackEcr="${StackEcr:-cinehub-lambda-ecr}"
ImageName="${ImageName:-cinehub}"
ImageTag="${ImageTag:-latest}"
Dockerfile="${Dockerfile:-Dockerfile.desacoplada}"
ContextDir="${ContextDir:-.}"
EcrUriOverride="${EcrUriOverride:-}"

echo "==> REGION:      $Region"
echo "==> STACK_ECR:   $StackEcr"
echo "==> IMAGE_NAME:  $ImageName"
echo "==> IMAGE_TAG:   $ImageTag"
echo "==> DOCKERFILE:  $Dockerfile"
echo "==> CONTEXT_DIR: $ContextDir"

AccountId=$(aws sts get-caller-identity --query Account --output text --region "$Region")
BaseEcr="${AccountId}.dkr.ecr.${Region}.amazonaws.com"

# Obtén el URI del repo (desde override o salida del stack)
if [ -n "$EcrUriOverride" ]; then
  RepoUri="$EcrUriOverride"
else
  RepoUri=$(aws cloudformation describe-stacks \
    --stack-name "$StackEcr" --region "$Region" \
    --query "Stacks[0].Outputs[?OutputKey=='RepositoryUri'].OutputValue" \
    --output text)
fi

if [ -z "$RepoUri" ] || [ "$RepoUri" = "None" ]; then
  echo "No pude obtener RepositoryUri. Revisa el stack $StackEcr o exporta EcrUriOverride" >&2
  exit 1
fi

echo "==> ACCOUNT_ID:  $AccountId"
echo "==> ECR BASE:    $BaseEcr"
echo "==> REPO_URI:    $RepoUri"

# Login ECR
echo "==> Login en ECR..."
aws ecr get-login-password --region "$Region" \
  | docker login --username AWS --password-stdin "$BaseEcr"

# Asegura builder de buildx
if ! docker buildx inspect cinehub_builder >/dev/null 2>&1; then
  echo "==> Creando builder cinehub_builder..."
  docker buildx create --use --name cinehub_builder
else
  docker buildx use cinehub_builder
fi

# Build & Push para linux/amd64 (sin provenance/SBOM para evitar manifest list)
echo "==> Construyendo y publicando imagen (linux/amd64)..."
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  --sbom=false \
  -f "$Dockerfile" \
  -t "${RepoUri}:${ImageTag}" \
  --push \
  "$ContextDir"

echo "✅ Imagen publicada exitosamente: ${RepoUri}:${ImageTag}"