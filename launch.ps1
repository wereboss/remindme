# ==============================================================================
# Cross-Platform Launcher for Windows PowerShell
# Notes & Reminders PWA (RemindMe)
# ==============================================================================

$ErrorActionPreference = "Stop"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Starting Notes & Reminders PWA Service " -ForegroundColor Cyan
Write-Host " Platform: Windows (PowerShell)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Find python
$pythonCmd = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $pythonCmd) {
    $pythonCmd = (Get-Command py -ErrorAction SilentlyContinue)
}

if (-not $pythonCmd) {
    Write-Error "Python was not found in PATH. Please install Python 3.10+ from https://www.python.org/."
    exit 1
}

# Create venv if needed
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment in .venv..." -ForegroundColor Yellow
    & $pythonCmd.Source -m venv .venv
}

# Activate
$venvActivate = Join-Path (Get-Location) ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
}

Write-Host "Verifying dependencies..." -ForegroundColor Yellow
pip install --quiet -r requirements.txt

$env:PORT = "9031"

Write-Host ""
Write-Host "RemindMe PWA is running on:" -ForegroundColor Green
Write-Host " -> Local:   http://localhost:9031" -ForegroundColor Green
Write-Host " -> Network: http://0.0.0.0:9031" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server." -ForegroundColor Gray
Write-Host ""

Start-Process "http://localhost:9031"
python run.py
