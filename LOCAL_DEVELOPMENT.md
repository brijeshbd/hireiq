# 🚀 HireIQ - Local Development Guide

## Quick Start (One Command)

Run everything with a single command from the project root:

```bash
./run-all.sh
```

This starts:
- ✅ **Backend API** on `http://localhost:8000`
- ✅ **Frontend React App** on `http://localhost:3000`

## What This Does

The `run-all.sh` script:
1. Checks for `.env` file in `ai-service/` (creates one if missing)
2. Installs Python dependencies (if needed)
3. Starts FastAPI backend with auto-reload
4. Installs npm packages (if needed)
5. Starts React frontend with auto-reload
6. Provides helpful URLs and instructions

## Prerequisites

Before running, make sure you have:

### Backend Requirements
- ✅ **Python 3.11+** - [Install](https://www.python.org/downloads/)
- ✅ **pip** - Usually comes with Python
- ✅ **Redis** (optional for local dev, but recommended)
  - Mac: `brew install redis` then `redis-server`
  - Ubuntu: `sudo apt-get install redis-server`
  - Docker: `docker run -d -p 6379:6379 redis`

### Frontend Requirements  
- ✅ **Node.js 18+** - [Install](https://nodejs.org/)
- ✅ **npm** - Usually comes with Node.js

## Environment Setup

### Backend (.env file)

The script creates `.env` automatically, but you need to add your API key:

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

Create `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
```

## Manual Setup (If you prefer)

### Start Backend Only

```bash
cd ai-service
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### Start Frontend Only

```bash
cd frontend
npm install  # Only needed first time
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

# View API docs
open http://localhost:8000/docs
```

## Stopping Services

Press `Ctrl+C` in the terminal - the script will gracefully stop both services.

## Troubleshooting

### "Port 8000 already in use"
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### "Port 3000 already in use"
```bash
# Find what's using port 3000
lsof -i :3000

# Kill it
kill -9 <PID>
```

### "Redis connection refused"
```bash
# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis
```

### "GROQ_API_KEY not set"
1. Get key from https://console.groq.com/
2. Update `ai-service/.env`
3. Restart backend: Stop and run `./run-all.sh` again

## File Structure

```
hireiq/
├── run-all.sh              ← Run this!
├── ai-service/             ← Backend (Python/FastAPI)
│   ├── api.py              ← Main API
│   ├── memory.py           ← Redis conversation storage
│   ├── requirements.txt
│   └── .env                ← Configure here
├── frontend/               ← Frontend (React)
│   ├── src/
│   ├── package.json
│   └── .env                ← Configure here
└── README.md
```

## Next Steps

- 📖 Read the main [README.md](README.md) for architecture details
- 🔍 Check API docs at http://localhost:8000/docs
- 🎨 Browse frontend at http://localhost:3000
- 🚀 Ready to deploy? See deployment guides

---

**Happy coding! 🎉**
