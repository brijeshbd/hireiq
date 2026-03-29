#!/bin/bash

# HireIQ - Lightweight startup script
# Use this if run-all.sh is hanging

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🚀 Starting HireIQ (Lightweight)..."
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}1️⃣  Starting Backend...${NC}"
cd ai-service
echo "   Using: python3.11 -m uvicorn api:app --port 8000"
python3.11 -m uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}   ✅ Started (PID: $BACKEND_PID)${NC}"
echo "   ⏳ Loading models (this may take 1-2 minutes on first run)..."
sleep 15

echo ""
echo -e "${BLUE}2️⃣  Starting Frontend...${NC}"
cd ../frontend
echo "   Using: npm start"
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}   ✅ Started (PID: $FRONTEND_PID)${NC}"

echo ""
echo -e "${GREEN}✅ Services started!${NC}"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop...${NC}"

# Keep running
wait
