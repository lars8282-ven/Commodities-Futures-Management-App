# Test Script Runner for CME Scraper
# Uses Anaconda Python to avoid venv issues

Write-Host "CME Scraper Test Runner" -ForegroundColor Green
Write-Host "Using Anaconda Python" -ForegroundColor Cyan
Write-Host ""

# Set Python path
$pythonPath = "C:\Users\LuisRodriguez\anaconda3\python.exe"

# Check if Python exists
if (-not (Test-Path $pythonPath)) {
    Write-Host "ERROR: Python not found at $pythonPath" -ForegroundColor Red
    Write-Host "Please update the pythonPath in this script." -ForegroundColor Yellow
    exit 1
}

# Run the test script
Write-Host "Running test_scraper.py..." -ForegroundColor Yellow
Write-Host ""

& $pythonPath test_scraper.py

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Test script exited with error code: $LASTEXITCODE" -ForegroundColor Red
} else {
    Write-Host ""
    Write-Host "Tests completed successfully!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

