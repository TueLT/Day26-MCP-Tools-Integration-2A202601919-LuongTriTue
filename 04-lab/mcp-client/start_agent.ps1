[CmdletBinding()]
param(
    [ValidateSet("Web", "Run")]
    [string]$Mode = "Web",
    [ValidateRange(1, 65535)]
    [int]$WebPort = 8000,
    [string]$Query = "Hãy gọi health_check và cho biết MCP server có hoạt động không."
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$envFile = Join-Path $repoRoot ".env"
$adk = Join-Path $PSScriptRoot ".venv\Scripts\adk.exe"

if (-not (Test-Path -LiteralPath $envFile)) {
    throw "Missing environment file: $envFile"
}

foreach ($line in Get-Content -LiteralPath $envFile) {
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
        $name = $Matches[1]
        $value = $Matches[2].Trim().Trim('"').Trim("'")
        if (-not [string]::IsNullOrWhiteSpace($value)) {
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

if (-not $env:GEMINI_API_KEY) {
    throw "GEMINI_API_KEY is missing in $envFile"
}

# ADK ưu tiên GOOGLE_API_KEY và đọc nó ngay khi CLI khởi động.
$env:GOOGLE_API_KEY = $env:GEMINI_API_KEY
$env:PYTHONUTF8 = "1"

Push-Location -LiteralPath $PSScriptRoot
try {
    if ($Mode -eq "Web") {
        & $adk web --port $WebPort
    }
    else {
        & $adk run --in_memory --jsonl --timeout 60s .\weather_agent $Query
    }

    if ($LASTEXITCODE -ne 0) {
        throw "ADK exited with code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}
