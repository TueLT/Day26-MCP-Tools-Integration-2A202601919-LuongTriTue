[CmdletBinding()]
param(
    [switch]$IncludeLab
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $repoRoot ".venv\Scripts\python.exe"

Push-Location -LiteralPath $repoRoot
try {
    if (-not (Test-Path -LiteralPath $venvPython)) {
        python -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create the root virtual environment."
        }
    }

    & $venvPython -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install root requirements."
    }

    if ($IncludeLab) {
        & $venvPython -m pip install uv
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install uv."
        }
        $uv = Join-Path $repoRoot ".venv\Scripts\uv.exe"

        Push-Location -LiteralPath (Join-Path $repoRoot "04-lab\mcp-server")
        try {
            & $uv sync --locked --link-mode copy
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to sync the lab MCP server environment."
            }
        }
        finally {
            Pop-Location
        }

        Push-Location -LiteralPath (Join-Path $repoRoot "04-lab\mcp-client")
        try {
            & $uv sync --locked --link-mode copy
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to sync the lab MCP client environment."
            }
        }
        finally {
            Pop-Location
        }
    }
}
finally {
    Pop-Location
}

Write-Host "Setup completed successfully."
