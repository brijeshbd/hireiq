# 🚀 HireIQ - Local Development Guide

## Quick Start (One Command)

Run everything with a single command from the project root:

```bash
./start-dev.sh
```

Or use the full featured version:

```bash
./run-all.sh
```

This starts:
- ✅ **Backend API** on `http://localhost:8000`
- ✅ **Frontend React App** on `http://localhost:3000`

## What This Does

The scripts:
1. Check prerequisites (Python 3.11+, Node.js 18+)
2. Install dependencies if needed
3. Start FastAPI backend with auto-reload
4. Start React frontend with auto-reload
5. Provide helpful URLs

## Prerequisites

Before running, ensure you have:

### Backend Requirements
- ✅ **Python 3.11+** (REQUIRED! Not 3.9 or 3.10)
  ```bash
  python3.11 --version
  ```
  Install: `brew install python@3.11`

- ✅ **Installed dependencies:**
  ```bash
  cd ai-service
  python3.11 -m pip install -r requirements.txt
  ```

### Frontend Requirements  
- ✅ **Node.js 18+** 
  ```bash
  node --version
  ```
  
- ✅ **npm 8+**
  ```bash
  npm --version
  ```

## Environment Setup

### Backend (.env file)

The script creates `ai-service/.env` automatically. Update it with your API key:

```bash
# Edit ai-service/.env
GROQ_API_KEY=sk_live_xxxxx  # Get from https://console.groq.com/

# These defaults work for local dev:
PORT=8000
REDIS_HOST=localhost
REDIS_PORT=6379
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hireiq
DB_USER=postgres
DB_PASSWORD=root
```

### Frontend (.env)

Frontend automatically detects the backend. No config needed!

## Manual Setup (Step by Step)

### Start Backend Only

```bash
cd ai-service
python3.11 -m pip install -r requirements.txt  # First time only
python3.11 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**First startup takes 1-2 minutes** (loads ML models)

### Start Frontend Only

```bash
cd frontend
npm install  # First time only
npm start
```

## Testing

Once everything is running:

```bash
# Test backend health
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello","session_id":"user-123"}'

# View API docs (interactive)
open http://localhost:8000/docs
```

## Stopping Services

Press `Ctrl+C` in the terminal - services will stop gracefully.

## Troubleshooting

### "Port 8000 already in use"
```bash
lsof -i :8000          # Find what's using it
kill -9 <PID>          # Kill the process
```

### "Port 3000 already in use"
```bash
lsof -i :3000
kill -9 <PID>
```

### Backend won't start / hangs
1. Check Python version: `python3.11 --version` (must be 3.11+)
2. Reinstall dependencies:
   ```bash
   cd ai-service
   python3.11 -m pip install -r requirements.txt --force-reinstall
   ```
3. Check logs: `tail -f /tmp/hireiq-backend.log`

### "GROQ_API_KEY not set"
1. Get key from https://console.groq.com/
2. Update `ai-service/.env`:
   ```
   GROQ_API_KEY=sk_live_xxxxx
   ```
3. Restart backend

### Frontend shows "Cannot reach API"
Make sure both are running:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

## File Structure

```
hireiq/
├── start-dev.sh            ← Simple startup
├── run-all.sh              ← Full-featured startup
├── check-setup.sh          ← Verify setup
├── SETUP.md                ← Complete guide
├── ai-service/             ← Backend (Python/FastAPI)
│   ├── api.py              ← Main API
│   ├── requirements.txt
│   └── .env                ← Configure here
├── frontend/               ← Frontend (React)
│   ├── src/
│   ├── package.json
│   └── public/
└── README.md
```

## Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/api/chat` | POST | Chat with AI |
| `/api/analyze-resume` | POST | Resume analysis |
| `/api/analyze-jd` | POST | Job description analysis |
| `/api/cover-letter` | POST | Cover letter generation |
| `/api/interview/start` | POST | Start interview |
| `/api/interview/answer` | POST | Submit interview answer |
| `/docs` | GET | API documentation (Swagger) |

## Quick Commands

```bash
# Setup checker
./check-setup.sh

# Start everything
./start-dev.sh          # Simple
./run-all.sh            # Full-featured

# Start backend only
cd ai-service && python3.11 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Start frontend only
cd frontend && npm start

# Test API
curl http://localhost:8000/health
```

## Next Steps

- 📖 Read the main [README.md](README.md) for architecture
- 🔍 Explore API docs at http://localhost:8000/docs
- 🎨 Visit frontend at http://localhost:3000
- � Check [SETUP.md](SETUP.md) for detailed setup guide

---

**Happy coding! 🎉**
