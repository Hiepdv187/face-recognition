#!/bin/bash

echo "🎥 Starting Smart Camera Face Recognition System"
echo "==============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "app_realtime.py" ]; then
    echo -e "${RED}❌ Error: app_realtime.py not found. Please run this script from face-recognition directory${NC}"
    exit 1
fi

# Check if smart camera file exists
if [ ! -f "smart_camera.html" ]; then
    echo -e "${RED}❌ Error: smart_camera.html not found. Please create the smart camera interface first${NC}"
    exit 1
fi

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
    echo -e "${YELLOW}⚠️  Golang project not found at ../golang-project${NC}"
    echo -e "${YELLOW}⚠️  Smart Camera will run without Golang integration${NC}"
else
    echo -e "${GREEN}✅ Golang project found${NC}"
fi

echo ""
echo -e "${GREEN}🎯 Starting Smart Camera System...${NC}"
echo ""

# Start Python Flask server
echo -e "${BLUE}📡 Starting Python Smart Camera Server...${NC}"
cd ../face-recognition
source venv/Scripts/activate
python app_realtime.py &
PYTHON_PID=$!
echo -e "${GREEN}✅ Python server started (PID: $PYTHON_PID)${NC}"

# Wait a moment for Python server to start
sleep 4

echo ""
echo -e "${GREEN}🎉 Smart Camera System started successfully!${NC}"
echo ""
echo -e "${YELLOW}🌐 Smart Camera URLs:${NC}"
echo "   • 🎥 Smart Camera:        http://localhost:5000/smart-camera"
echo "   • 📹 Real-time Recognition: http://localhost:5000/realtime"
echo "   • 📹 Webcam Interface:     http://localhost:5000/webcam"
echo "   • 🏠 Homepage:            http://localhost:5000/"
echo ""
echo -e "${YELLOW}📡 API Endpoints:${NC}"
echo "   POST http://localhost:5000/api/face/register  - Register new face"
echo "   POST http://localhost:5000/api/face/recognize - Recognize face"
echo "   GET  http://localhost:5000/api/face/persons   - Get all persons"
echo ""
echo -e "${YELLOW}🎥 Smart Camera Features:${NC}"
echo "   ✅ Real-time face recognition with overlay"
echo "   ✅ Automatic capture and recognition"
echo "   ✅ Live statistics and confidence scoring"
echo "   ✅ Visual feedback on camera feed"
echo "   ✅ Face registration with live preview"
echo ""
echo -e "${YELLOW}📱 How to use:${NC}"
echo "   1. Open http://localhost:5000/smart-camera"
echo "   2. Click 'Start Camera' to activate webcam"
echo "   3. Position your face in the detection frame"
echo "   4. See recognition results on camera feed!"
echo "   5. Click 'Register Face' to add new faces"
echo ""
echo -e "${YELLOW}🔄 To stop the system:${NC}"
echo "   Press Ctrl+C or run: kill $PYTHON_PID"
echo ""

# Wait for user to stop
trap 'echo -e "\n${YELLOW}🛑 Stopping Smart Camera System...${NC}"; kill $PYTHON_PID; exit 0' INT

# Keep script running
wait
