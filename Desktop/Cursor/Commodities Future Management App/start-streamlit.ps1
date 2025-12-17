# Streamlit Startup Script
cd "C:\Users\LuisRodriguez\Desktop\Cursor\Commodities Future Management App"

# Set environment variables
$env:INSTANT_APP_ID = "a72f835b-06f6-4031-a6c2-9668bb3832bf"
$env:NEXTJS_API_URL = "http://localhost:3000/api"

Write-Host "Starting Streamlit..." -ForegroundColor Green
Write-Host "Working Directory: $(Get-Location)" -ForegroundColor Cyan
Write-Host "Python: .\venv\Scripts\python.exe" -ForegroundColor Cyan
Write-Host ""

# Start Streamlit
.\venv\Scripts\python.exe -m streamlit run app.py

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Streamlit exited with error code: $LASTEXITCODE" -ForegroundColor Red
    Write-Host "Press any key to close..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

