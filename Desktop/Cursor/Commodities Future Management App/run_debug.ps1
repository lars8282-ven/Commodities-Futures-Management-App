# Debug Script Runner for CME Scraper
# Runs in visible mode so you can see what's happening

Write-Host "CME Scraper Debug Tool" -ForegroundColor Green
Write-Host "This will open a browser window - you can watch it work!" -ForegroundColor Cyan
Write-Host ""

# Set Python path
$pythonPath = "C:\Users\LuisRodriguez\anaconda3\python.exe"

# Check if Python exists
if (-not (Test-Path $pythonPath)) {
    Write-Host "ERROR: Python not found at $pythonPath" -ForegroundColor Red
    Write-Host "Please update the pythonPath in this script." -ForegroundColor Yellow
    exit 1
}

# Run the debug script
Write-Host "Running debug_scraper.py..." -ForegroundColor Yellow
Write-Host ""

& $pythonPath debug_scraper.py

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Debug script exited with error code: $LASTEXITCODE" -ForegroundColor Red
} else {
    Write-Host ""
    Write-Host "Debug complete!" -ForegroundColor Green
}

Write-Host ""
Write-Host "Press any key to close..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

