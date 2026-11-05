# Quick test of the LLM credentials configured in .env
# Usage:  .\test_llm_key.ps1   (from pqr_system/backend)
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$envFile = Join-Path $PSScriptRoot ".env"
if (-not (Test-Path $envFile)) { Write-Error ".env not found at $envFile"; exit 1 }

$settings = @{}
Get-Content $envFile -Encoding UTF8 | ForEach-Object {
    if ($_ -match "^\s*([^#=\s]+)\s*=\s*(.*)$") { $settings[$Matches[1]] = $Matches[2].Trim() }
}

$key     = $settings["PQR_OPENAI_API_KEY"]
$baseUrl = $settings["PQR_OPENAI_BASE_URL"]
$model   = $settings["PQR_OPENAI_MODEL"]

if (-not $key -or -not $baseUrl -or -not $model) {
    Write-Error "Missing PQR_OPENAI_API_KEY / PQR_OPENAI_BASE_URL / PQR_OPENAI_MODEL in .env"
    exit 1
}

Write-Host "Endpoint: $baseUrl"
Write-Host "Model:    $model"
Write-Host "Key:      $($key.Substring(0,8))... ($($key.Length) chars)"

$body = @{
    model    = $model
    messages = @(@{ role = "user"; content = "Responde solo con: OK" })
    max_tokens = 10
} | ConvertTo-Json -Depth 5

try {
    $resp = Invoke-WebRequest -Uri "$($baseUrl.TrimEnd('/'))/chat/completions" -Method Post `
        -Headers @{ "Authorization" = "Bearer $key" } `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) `
        -ContentType "application/json; charset=utf-8" -TimeoutSec 60 -UseBasicParsing
    $r = [System.Text.Encoding]::UTF8.GetString($resp.RawContentStream.ToArray()) | ConvertFrom-Json
    Write-Host "`nSUCCESS - server responded with model '$($r.model)'" -ForegroundColor Green
    Write-Host "Response: $($r.choices[0].message.content)"
} catch {
    Write-Host "`nFAILED" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Body:   $($_.ErrorDetails.Message)"
    exit 1
}
