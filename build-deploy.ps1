Param(
  [string]$Region = "us-east-1",
  [string]$StackEcr = "cinehub-ecr",
  [string]$ImageName = "cinehub",
  [string]$ImageTag = "latest",
  [string]$Dockerfile = "Dockerfile",
  [string]$ContextDir = ".",
  [string]$EcrUriOverride = ""
)

$ErrorActionPreference = "Stop"

Write-Host "==> REGION:      $Region"
Write-Host "==> STACK_ECR:   $StackEcr"
Write-Host "==> IMAGE_NAME:  $ImageName"
Write-Host "==> IMAGE_TAG:   $ImageTag"
Write-Host "==> DOCKERFILE:  $Dockerfile"
Write-Host "==> CONTEXT_DIR: $ContextDir"

$AccountId = aws sts get-caller-identity --query Account --output text --region $Region
$BaseEcr   = "$AccountId.dkr.ecr.$Region.amazonaws.com"

if ($EcrUriOverride -ne "") {
  $RepoUri = $EcrUriOverride
} else {
  $RepoUri = aws cloudformation describe-stacks `
    --stack-name $StackEcr --region $Region `
    --query "Stacks[0].Outputs[?OutputKey=='RepositoryUri'].OutputValue" `
    --output text
}

if ([string]::IsNullOrEmpty($RepoUri) -or $RepoUri -eq "None") {
  throw "No pude obtener RepositoryUri. Revisa el stack $StackEcr u ofrece -EcrUriOverride"
}

Write-Host "==> ACCOUNT_ID:  $AccountId"
Write-Host "==> ECR BASE:    $BaseEcr"
Write-Host "==> REPO_URI:    $RepoUri"

aws ecr get-login-password --region $Region `
  | docker login --username AWS --password-stdin $BaseEcr | Out-Null

docker build -f $Dockerfile -t "$ImageName`:$ImageTag" $ContextDir
docker tag "$ImageName`:$ImageTag" "$RepoUri`:$ImageTag"
docker push "$RepoUri`:$ImageTag"

Write-Host "✅ Push completado."
