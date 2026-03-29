# 🚀 HireIQ - Local Development Setup

## Quick Start (One Command)

Run everything with a single command:

```bash
./run-all.sh
```

or

```bash
./quick-start.sh
```

**Note:** First run loads ML models and takes 1-2 minutes. Subsequent runs are faster.

This will start:
- ✅ **Frontend** (React) - `http://localhost:3000`
- ✅ **Backend API** (FastAPI) - `http://localhost:8000`

---

## Prerequisites

- **Python 3.11+** (Required!) - Check: `python3.11 --version`
- **Node.js 18+** - Check: `node --version`

**Install Python 3.11 if needed:**
```bash
# macOS with Homebrew
brew install python@3.11

# Or use pyenv
pyenv install 3.11.15
```

### 1️⃣ Backend (FastAPI) - Port 8000

```bash
# Navigate to backend
cd ai-service

# Create .env file (if not exists)
cat > .env << EOF
PORT=8000
GROQ_API_KEY=your-actual-key-here
REDIS_HOST=localhost
REDIS_PORT=6379
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hireiq
DB_USER=postgres
DB_PASSWORD=root
EOF

# Install dependencies (Python 3.11 required!)
python3.11 -m pip install -r requirements.txt

# Start backend (first run loads ML models - may take 1-2 min)
python3.11 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Output should show:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**API Docs:** http://localhost:8000/docs

---

### 2️⃣ Frontend (React) - Port 3000

In a **new terminal**:

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start frontend
npm start
```

Frontend will auto-open at: http://localhost:3000

---

## 🔗 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/chat` | POST | Chat with AI |
| `/api/analyze-resume` | POST | Resume analysis |
| `/api/analyze-jd` | POST | Job description analysis |
| `/api/cover-letter` | POST | Generate cover letter |
| `/api/interview/start` | POST | Start interview |
| `/api/interview/answer` | POST | Submit interview answer |

---

## 🛑 Stop Services

Press **Ctrl+C** in each terminal, or:

```bash
pkill -f uvicorn          # Stop backend
pkill -f "npm start"      # Stop frontend
```

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# If stuck, force kill
pkill -f uvicorn
```

### Frontend won't start
```bash
# Check if port 3000 is in use
lsof -i :3000

# If stuck, force kill
pkill -f "npm start"
```

### Dependencies not found
```bash
# Reinstall all dependencies
pip3 install -r ai-service/requirements.txt --force-reinstall
cd frontend && npm install --force
```

### GROQ_API_KEY errors
1. Get your key from: https://console.groq.com/
2. Add to `ai-service/.env`:
   ```
   GROQ_API_KEY=sk_live_xxxxx
   ```
3. Restart backend

---

## 📝 Environment Variables

**Backend** (`ai-service/.env`):
- `GROQ_API_KEY` - Your Groq API key (required for AI features)
- `REDIS_HOST` - Redis server (default: localhost)
- `REDIS_PORT` - Redis port (default: 6379)
- `DB_*` - PostgreSQL connection details

**Frontend** (`frontend/.env`):
- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:8000)

---

## 🚀 Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Railway/Vercel setup

