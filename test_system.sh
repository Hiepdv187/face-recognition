#!/bin/bash

echo "🧪 Testing Combined Face Recognition + Golang System"
echo "======================================================"
echo ""

# Test Face Recognition Service
echo "📱 Face Recognition Service (Port 5000):"
if curl -f -s http://localhost:5000/health > /dev/null; then
    echo "✅ Running - Health check passed"
    curl -s http://localhost:5000/health | python3 -m json.tool
else
    echo "❌ Not responding"
fi
echo ""

# Test Golang Service
echo "🚀 Golang Service (Port 8080):"
if curl -f -s http://localhost:8080/health > /dev/null; then
    echo "✅ Running - Health check passed"
    curl -s http://localhost:8080/health | python3 -m json.tool
else
    echo "❌ Not responding"
fi
echo ""

# Test Nginx Gateway
echo "🌐 Nginx Gateway (Port 80):"
if curl -f -s http://localhost/health > /dev/null; then
    echo "✅ Running - Gateway working"
    curl -s http://localhost/health | python3 -m json.tool
else
    echo "❌ Not responding or not configured properly"
fi
echo ""

# Test Face API through Nginx
echo "🔗 Face API through Nginx (/api/face/):"
if curl -f -s http://localhost/api/face/health > /dev/null; then
    echo "✅ Running - Face API accessible through gateway"
else
    echo "❌ Not accessible through gateway"
fi
echo ""

# Test Golang API through Nginx
echo "🔗 Golang API through Nginx (/api/go/):"
if curl -f -s http://localhost/api/go/health > /dev/null; then
    echo "✅ Running - Golang API accessible through gateway"
else
    echo "❌ Not accessible through gateway"
fi
echo ""

echo "📋 System Status Summary:"
echo "========================="
docker-compose ps
echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "• Main Interface: http://localhost"
echo "• Face API Direct: http://localhost:5000"
echo "• Golang API Direct: http://localhost:8080"
echo "• Face API via Nginx: http://localhost/api/face/"
echo "• Golang API via Nginx: http://localhost/api/go/"
echo "• Health Check: http://localhost/health"
