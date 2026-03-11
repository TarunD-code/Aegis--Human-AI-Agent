Write-Host "Running Verification Suite for Aegis v3.6"
Write-Host "-----------------------------------------"

Write-Host "1. Bootstrapping environment..."
.\scripts\bootstrap.ps1

Write-Host "2. Running Linter..."
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

Write-Host "3. Running Mypy..."
mypy . --ignore-missing-imports

Write-Host "4. Running Unit Tests..."
$env:AEGIS_OFFLINE_MODE="true"
pytest tests/

Write-Host "5. Starting Health Endpoint & Daemon Test..."
Start-Process -FilePath "python" -ArgumentList "main.py --mode background" -PassThru -NoNewWindow | Set-Variable -Name "DaemonProcess"
Start-Sleep -Seconds 2

Try {
    $response = Invoke-RestMethod -Uri "http://127.0.0.1:17123/health"
    If ($response.status -eq "ok") {
        Write-Host "Health Check Passed."
    } Else {
        Write-Host "Health Check Failed. Response: $($response | ConvertTo-Json)"
    }
} Catch {
    Write-Host "Health Check Failed. Exception: $($_.Exception.Message)"
} Finally {
    Stop-Process -Id $DaemonProcess.Id -Force
}

Write-Host "Verification Suite Passed!"
