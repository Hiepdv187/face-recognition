Write-Host "🚀 Starting Complete Face Recognition System" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app_realtime.py")) {
    Write-Host "❌ Error: app_realtime.py not found. Please run this script from face-recognition directory" -ForegroundColor Red
    exit 1
}

Write-Host "🔍 Checking Python environment..." -ForegroundColor Blue
if (-not (Test-Path "venv")) {
    Write-Host "⚠️  Python virtual environment not found. Creating..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
} else {
    Write-Host "✅ Python virtual environment found" -ForegroundColor Green
}

# Check Go environment
Write-Host "🔍 Checking Go environment..." -ForegroundColor Blue
if (-not (Test-Path "../golang-project/main.go")) {
    Write-Host "❌ Error: Golang project not found at ../golang-project" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Golang project found" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 Starting services..." -ForegroundColor Green
Write-Host ""

# Start Python Flask server in background
Write-Host "📡 Starting Python Face Recognition Server..." -ForegroundColor Blue
Start-Process python -ArgumentList "app_realtime.py" -NoNewWindow
$PYTHON_PID = (Get-Process python).Id
Write-Host "✅ Python server started (PID: $PYTHON_PID)" -ForegroundColor Green

# Wait a moment for Python server to start
Start-Sleep -Seconds 3

# Start Golang server
Write-Host "🚀 Starting Golang HTTP Server..." -ForegroundColor Blue
Set-Location ../golang-project
Start-Process go -ArgumentList "run main.go controllers.go" -NoNewWindow
$GOLANG_PID = (Get-Process -Name "main" -ErrorAction SilentlyContinue).Id
if ($GOLANG_PID) {
    Write-Host "✅ Golang server started (PID: $GOLANG_PID)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Warning: Could not get Golang PID, but server may still be running" -ForegroundColor Yellow
}

# Wait a moment for Golang server to start
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "🎉 All services started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Yellow
Write-Host "   • Python Face Recognition: http://localhost:5000" -ForegroundColor White
Write-Host "   • Golang HTTP Server:      http://localhost:8080" -ForegroundColor White
Write-Host "   • 🎥 Smart Camera:         http://localhost:5000/smart-camera (NEW)" -ForegroundColor White
Write-Host "   • 📹 Real-time Recognition: http://localhost:5000/realtime" -ForegroundColor White
Write-Host "   • 📹 Webcam Interface:     http://localhost:5000/webcam" -ForegroundColor White
Write-Host "   • 🏠 Health Check:         http://localhost:5000/health" -ForegroundColor White
Write-Host ""
Write-Host "📡 API Endpoints:" -ForegroundColor Yellow
Write-Host "   POST http://localhost:5000/api/face/register  - Register new face" -ForegroundColor White
Write-Host "   POST http://localhost:5000/api/face/recognize - Recognize face" -ForegroundColor White
Write-Host "   GET  http://localhost:5000/api/face/persons   - Get all persons" -ForegroundColor White
Write-Host ""
Write-Host "🔄 To stop all services:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C or run: Stop-Process -Id $PYTHON_PID" -ForegroundColor White
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host ""
    Write-Host "🛑 Stopping services..." -ForegroundColor Yellow
    if ($PYTHON_PID) {
        Stop-Process -Id $PYTHON_PID -Force -ErrorAction SilentlyContinue
    }
    if ($GOLANG_PID) {
        Stop-Process -Id $GOLANG_PID -Force -ErrorAction SilentlyContinue
    }
    exit 0
}
