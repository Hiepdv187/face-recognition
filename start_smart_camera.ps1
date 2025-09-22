Write-Host "🎥 Starting Smart Camera Face Recognition System" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app_realtime.py")) {
    Write-Host "❌ Error: app_realtime.py not found. Please run this script from face-recognition directory" -ForegroundColor Red
    exit 1
}

# Check if smart camera file exists
if (-not (Test-Path "smart_camera.html")) {
    Write-Host "❌ Error: smart_camera.html not found. Please create the smart camera interface first" -ForegroundColor Red
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
    Write-Host "⚠️  Golang project not found at ../golang-project" -ForegroundColor Yellow
    Write-Host "⚠️  Smart Camera will run without Golang integration" -ForegroundColor Yellow
} else {
    Write-Host "✅ Golang project found" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎯 Starting Smart Camera System..." -ForegroundColor Green
Write-Host ""

# Start Python Flask server
Write-Host "📡 Starting Python Smart Camera Server..." -ForegroundColor Blue
Start-Process python -ArgumentList "app_realtime.py" -NoNewWindow
$PYTHON_PID = (Get-Process python).Id
Write-Host "✅ Python server started (PID: $PYTHON_PID)" -ForegroundColor Green

# Wait a moment for Python server to start
Start-Sleep -Seconds 4

Write-Host ""
Write-Host "🎉 Smart Camera System started successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Smart Camera URLs:" -ForegroundColor Yellow
Write-Host "   • 🎥 Smart Camera:        http://localhost:5000/smart-camera" -ForegroundColor White
Write-Host "   • 📹 Real-time Recognition: http://localhost:5000/realtime" -ForegroundColor White
Write-Host "   • 📹 Webcam Interface:     http://localhost:5000/webcam" -ForegroundColor White
Write-Host "   • 🏠 Homepage:            http://localhost:5000/" -ForegroundColor White
Write-Host ""
Write-Host "📡 API Endpoints:" -ForegroundColor Yellow
Write-Host "   POST http://localhost:5000/api/face/register  - Register new face" -ForegroundColor White
Write-Host "   POST http://localhost:5000/api/face/recognize - Recognize face" -ForegroundColor White
Write-Host "   GET  http://localhost:5000/api/face/persons   - Get all persons" -ForegroundColor White
Write-Host ""
Write-Host "🎥 Smart Camera Features:" -ForegroundColor Yellow
Write-Host "   ✅ Real-time face recognition with overlay" -ForegroundColor White
Write-Host "   ✅ Automatic capture and recognition" -ForegroundColor White
Write-Host "   ✅ Live statistics and confidence scoring" -ForegroundColor White
Write-Host "   ✅ Visual feedback on camera feed" -ForegroundColor White
Write-Host "   ✅ Face registration with live preview" -ForegroundColor White
Write-Host ""
Write-Host "📱 How to use:" -ForegroundColor Yellow
Write-Host "   1. Open http://localhost:5000/smart-camera" -ForegroundColor White
Write-Host "   2. Click 'Start Camera' to activate webcam" -ForegroundColor White
Write-Host "   3. Position your face in the detection frame" -ForegroundColor White
Write-Host "   4. See recognition results on camera feed!" -ForegroundColor White
Write-Host "   5. Click 'Register Face' to add new faces" -ForegroundColor White
Write-Host ""
Write-Host "🔄 To stop the system:" -ForegroundColor Yellow
Write-Host "   Press Ctrl+C or run: Stop-Process -Id $PYTHON_PID" -ForegroundColor White
Write-Host ""

# Keep script running
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} catch {
    Write-Host ""
    Write-Host "🛑 Stopping Smart Camera System..." -ForegroundColor Yellow
    if ($PYTHON_PID) {
        Stop-Process -Id $PYTHON_PID -Force -ErrorAction SilentlyContinue
    }
    exit 0
}
