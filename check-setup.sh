#!/bin/bash

# HireIQ - Environment Setup Checker
# Run this before starting the app

echo "🔍 Checking HireIQ Setup Requirements..."
echo ""

# Check Python 3.11
echo "📍 Python Version:"
if command -v python3.11 &> /dev/null; then
    PYTHON_VERSION=$(python3.11 --version)
    echo "   ✅ $PYTHON_VERSION"
else
    echo "   ❌ Python 3.11 not found!"
    echo "      Install: brew install python@3.11"
    exit 1
fi

# Check Node.js
echo ""
echo "📍 Node.js Version:"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "   ✅ $NODE_VERSION"
else
    echo "   ❌ Node.js not found!"
    echo "      Install: brew install node"
    exit 1
fi

# Check npm
echo ""
echo "📍 npm Version:"
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "   ✅ $NPM_VERSION"
else
    echo "   ❌ npm not found!"
    exit 1
fi

# Check if .env exists
echo ""
echo "📍 Backend Environment (.env):"
if [ -f "ai-service/.env" ]; then
    echo "   ✅ .env file exists"
    if grep -q "GROQ_API_KEY" ai-service/.env; then
        if grep "GROQ_API_KEY=your-" ai-service/.env > /dev/null; then
            echo "   ⚠️  GROQ_API_KEY not configured!"
            echo "      Edit ai-service/.env and add your Groq API key"
        else
            echo "   ✅ GROQ_API_KEY configured"
        fi
    fi
else
    echo "   ⚠️  .env file not found"
    echo "      Will be created when you run ./run-all.sh"
fi

# Check backend dependencies
echo ""
echo "📍 Backend Dependencies:"
if python3.11 -c "import fastapi" 2>/dev/null; then
    echo "   ✅ FastAPI installed"
else
    echo "   ❌ FastAPI not installed"
    echo "      Run: cd ai-service && python3.11 -m pip install -r requirements.txt"
    exit 1
fi

if python3.11 -c "import redis" 2>/dev/null; then
    echo "   ✅ Redis client installed"
else
    echo "   ❌ Redis client not installed"
    exit 1
fi

# Check frontend dependencies
echo ""
echo "📍 Frontend Dependencies:"
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ npm packages installed"
else
    echo "   ⚠️  npm packages not installed"
    echo "      Will be installed when you run ./run-all.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Setup check complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🚀 Ready to run: ./run-all.sh"
echo ""
