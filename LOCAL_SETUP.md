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

This will start:
- ✅ **Frontend** (React) - `http://localhost:3000`
- ✅ **Backend API** (FastAPI) - `http://localhost:8000`

---

## Manual Setup (Step by Step)

### Prerequisites

- **Python 3.9+** - Run: `python3 --version`
- **Node.js 18+** - Run: `node --version` & `npm --version`

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

# Install dependencies
pip3 install -r requirements.txt

# Start backend
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Test backend:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok","service":"HireIQ API","version":"1.0.0"}
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

