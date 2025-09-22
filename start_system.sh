#!/bin/bash

echo "🚀 Starting Complete Face Recognition System"
echo "============================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python environment
echo -e "${BLUE}🔍 Checking Python environment...${NC}"
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Python virtual environment not found. Creating...${NC}"
    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
else
    echo -e "${GREEN}✅ Python virtual environment found${NC}"
fi

# Check Go environment
echo -e "${BLUE}🔍 Checking Go environment...${NC}"
if [ ! -f "../golang-project/main.go" ]; then
    echo -e "${RED}❌ Error: Golang project not found at ../golang-project${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Golang project found${NC}"
fi

# Start services
echo ""
echo -e "${GREEN}🎯 Starting services...${NC}"
echo ""

# Start Python Flask server in background
echo -e "${BLUE}📡 Starting Python Face Recognition Server...${NC}"
cd ../face-recognition
source venv/Scripts/activate
python app_realtime.py &
PYTHON_PID=$!
echo -e "${GREEN}✅ Python server started (PID: $PYTHON_PID)${NC}"

# Wait a moment for Python server to start
sleep 3

# Start Golang server
echo -e "${BLUE}🚀 Starting Golang HTTP Server...${NC}"
cd ../golang-project
go run main.go controllers.go &
GOLANG_PID=$!
echo -e "${GREEN}✅ Golang server started (PID: $GOLANG_PID)${NC}"

# Wait a moment for Golang server to start
sleep 2

echo ""
echo -e "${GREEN}🎉 All services started successfully!${NC}"
echo ""
echo -e "${YELLOW}🌐 Access URLs:${NC}"
echo "   • Python Face Recognition: http://localhost:5000"
echo "   • Golang HTTP Server:      http://localhost:8080"
echo "   • 🎥 Smart Camera:         http://localhost:5000/smart-camera (NEW)"
echo "   • 📹 Real-time Recognition: http://localhost:5000/realtime"
echo "   • 📹 Webcam Interface:     http://localhost:5000/webcam"
echo "   • 🏠 Health Check:         http://localhost:5000/health"
echo ""
echo -e "${YELLOW}📡 API Endpoints:${NC}"
echo "   POST http://localhost:5000/api/face/register  - Register new face"
echo "   POST http://localhost:5000/api/face/recognize - Recognize face"
echo "   GET  http://localhost:5000/api/face/persons   - Get all persons"
echo ""
echo -e "${YELLOW}🔄 To stop all services:${NC}"
echo "   Press Ctrl+C or run: kill $PYTHON_PID $GOLANG_PID"
echo ""

# Wait for user to stop
trap 'echo -e "\n${YELLOW}🛑 Stopping services...${NC}"; kill $PYTHON_PID $GOLANG_PID; exit 0' INT

# Keep script running
wait
