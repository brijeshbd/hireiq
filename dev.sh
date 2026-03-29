#!/bin/zsh
# HireIQ - Ultra-simple one-liner startup
# Usage: source dev.sh
# Then just type: dev

function dev() {
    cd "$(git rev-parse --show-toplevel)" 2>/dev/null || cd . 
    echo "🚀 Starting HireIQ..."
    (cd ai-service && python -m uvicorn api:app --reload --port 8000) & \
    (cd frontend && npm start) & \
    wait
}

export -f dev
echo "✅ Type 'dev' to start everything"
