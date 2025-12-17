# Startup script for Commodities Futures Management App
# This script starts both the Next.js API server and Streamlit app

Write-Host "Starting Commodities Futures Management App..." -ForegroundColor Green
Write-Host ""

# Set environment variables
$env:NEXT_PUBLIC_INSTANT_APP_ID = "a72f835b-06f6-4031-a6c2-9668bb3832bf"
$env:INSTANT_APP_ID = "a72f835b-06f6-4031-a6c2-9668bb3832bf"
$env:NEXTJS_API_URL = "http://localhost:3000/api"

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$nextjsDir = Join-Path $scriptDir "commodities-futures-management-app"

Write-Host "Starting Next.js API server on port 3000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$nextjsDir'; `$env:NEXT_PUBLIC_INSTANT_APP_ID='a72f835b-06f6-4031-a6c2-9668bb3832bf'; npm run dev"

Write-Host "Waiting for Next.js to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host "Starting Streamlit app on port 8501..." -ForegroundColor Yellow
$venvPython = Join-Path $scriptDir "venv\Scripts\streamlit.exe"
if (Test-Path $venvPython) {
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptDir'; `$env:INSTANT_APP_ID='a72f835b-06f6-4031-a6c2-9668bb3832bf'; `$env:NEXTJS_API_URL='http://localhost:3000/api'; & '$venvPython' run app.py"
} else {
    Write-Host "Error: Streamlit not found at $venvPython" -ForegroundColor Red
    Write-Host "Please ensure the virtual environment is set up correctly." -ForegroundColor Red
}

Write-Host ""
Write-Host "Both servers are starting in separate windows." -ForegroundColor Green
Write-Host "Next.js API: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Streamlit App: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this script (servers will continue running)..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

