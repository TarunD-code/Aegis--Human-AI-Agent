$ErrorActionPreference = 'Stop'

Write-Host "Bootstrapping Aegis environment..."
If (-Not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
Write-Host "Environment ready."
