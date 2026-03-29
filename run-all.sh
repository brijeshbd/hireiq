#!/bin/bash

# HireIQ - Run all services (Frontend + Backend API)
# Usage: ./run-all.sh

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🚀 Starting HireIQ Stack from: $PROJECT_DIR"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print section headers
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
}

# Start Backend API (Python FastAPI)
print_header "Starting Backend API (Port 8000)"
cd "$PROJECT_DIR/ai-service"

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found in ai-service/. Creating one...${NC}"
    cat > .env << EOF
PORT=8000
GROQ_API_KEY=your-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hireiq
DB_USER=postgres
DB_PASSWORD=root
EOF
    echo -e "${YELLOW}Created .env - update GROQ_API_KEY!${NC}"
fi

# Start backend in background
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
sleep 2
echo ""

# Start Frontend (React)
print_header "Starting Frontend (Port 3000)"
cd "$PROJECT_DIR/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing npm dependencies...${NC}"
    npm install
fi

# Start frontend in background
npm start &
FRONTEND_PID=$!
echo -e "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
echo ""

# Print access URLs
print_header "Services Running 🎉"
echo -e "${GREEN}Frontend:  http://localhost:3000${NC}"
echo -e "${GREEN}Backend:   http://localhost:8000${NC}"
echo -e "${GREEN}Docs:      http://localhost:8000/docs${NC}"
echo -e "${GREEN}Health:    http://localhost:8000/health${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Handle Ctrl+C
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e "\n${YELLOW}Services stopped${NC}"; exit 0' INT

# Keep script running
wait
