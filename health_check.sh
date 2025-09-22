#!/bin/bash

# Health Check Script for Combined Services
# Usage: ./health_check.sh [service]

SERVICE=${1:-all}

echo "🔍 Checking health of services..."
echo "================================="

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "face-recognition" ]; then
    echo "📱 Face Recognition Service (Port 5000):"
    curl -f http://localhost:5000/health || echo "❌ Service not responding"
    echo ""
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "golang" ]; then
    echo "🚀 Golang Service (Port 8080):"
    curl -f http://localhost:8080/health || echo "❌ Service not responding"
    echo ""
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "nginx" ]; then
    echo "🌐 Nginx Gateway (Port 80):"
    curl -f http://localhost/health || echo "❌ Gateway not responding"
    echo ""
fi

if [ "$SERVICE" = "all" ] || [ "$SERVICE" = "postgres" ]; then
    echo "🗄️  PostgreSQL Database (Port 5432):"
    docker exec shared_postgres pg_isready -U app_user -d face_recognition_app || echo "❌ Database not responding"
    echo ""
fi

echo "✅ Health check completed!"
