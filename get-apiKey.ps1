param(
    [string]$ApiKeyID
)

aws apigateway get-api-key --api-key $ApiKeyID --include-value