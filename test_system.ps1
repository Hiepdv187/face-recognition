Write-Host "🧪 Testing Combined Face Recognition + Golang System" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""

# Test Face Recognition Service
Write-Host "📱 Face Recognition Service (Port 5000):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
    Write-Host "✅ Running - Health check passed" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "❌ Not responding" -ForegroundColor Red
}
Write-Host ""

# Test Golang Service
Write-Host "🚀 Golang Service (Port 8080):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing
    Write-Host "✅ Running - Health check passed" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "❌ Not responding" -ForegroundColor Red
}
Write-Host ""

# Test Nginx Gateway
Write-Host "🌐 Nginx Gateway (Port 80):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing
    Write-Host "✅ Running - Gateway working" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json
} catch {
    Write-Host "❌ Not responding or not configured properly" -ForegroundColor Red
}
Write-Host ""

# Test Face API through Nginx
Write-Host "🔗 Face API through Nginx (/api/face/):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/face/health" -UseBasicParsing
    Write-Host "✅ Running - Face API accessible through gateway" -ForegroundColor Green
} catch {
    Write-Host "❌ Not accessible through gateway" -ForegroundColor Red
}
Write-Host ""

# Test Golang API through Nginx
Write-Host "🔗 Golang API through Nginx (/api/go/):" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost/api/go/health" -UseBasicParsing
    Write-Host "✅ Running - Golang API accessible through gateway" -ForegroundColor Green
} catch {
    Write-Host "❌ Not accessible through gateway" -ForegroundColor Red
}
Write-Host ""

Write-Host "📋 System Status Summary:" -ForegroundColor Yellow
Write-Host "=========================" -ForegroundColor Yellow
docker-compose ps
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Magenta
Write-Host "===============" -ForegroundColor Magenta
Write-Host "• Main Interface: http://localhost" -ForegroundColor White
Write-Host "• Face API Direct: http://localhost:5000" -ForegroundColor White
Write-Host "• Golang API Direct: http://localhost:8080" -ForegroundColor White
Write-Host "• Face API via Nginx: http://localhost/api/face/" -ForegroundColor White
Write-Host "• Golang API via Nginx: http://localhost/api/go/" -ForegroundColor White
Write-Host "• Health Check: http://localhost/health" -ForegroundColor White
