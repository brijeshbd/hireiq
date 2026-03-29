# 🎯 HireIQ - Complete Local Setup Guide

## ⚡ TL;DR - Run Everything Locally

```bash
# Step 1: Check everything is installed
./check-setup.sh

# Step 2: Run everything (Frontend + Backend)
./run-all.sh

# Done! Open: http://localhost:3000
```

---

## 📋 What You Need

- **Python 3.11+** ⭐ (MUST be 3.11, not 3.9 or 3.10)
- **Node.js 18+**
- **npm 8+**

---

## 🔧 Installation Steps

### 1. Install Python 3.11

**macOS (Homebrew):**
```bash
brew install python@3.11
```

**Verify:**
```bash
python3.11 --version  # Should show: Python 3.11.x
```

### 2. Install Node.js (if not already installed)

**macOS:**
```bash
brew install node
```

**Verify:**
```bash
node --version   # Should show: v18+ or higher
npm --version    # Should show: 8+ or higher
```

---

## 🚀 Running HireIQ Locally

### Option A: One Command (Recommended)

```bash
cd ~/Documents/projects/python/hireiq
./run-all.sh
```

This starts **both Frontend + Backend** in parallel.

**Output:**
```
🚀 HireIQ - Starting all services...
1️⃣  Starting Backend API (FastAPI)...
   ✅ Backend started (PID: 12345)
   (First start loads ML models - may take 1-2 minutes)

2️⃣  Starting Frontend (React)...
   ✅ Frontend started (PID: 12346)

✅ All services running!
📱 Frontend:  http://localhost:3000
🔌 Backend:   http://localhost:8000
📚 API Docs:  http://localhost:8000/docs
Health:      http://localhost:8000/health
```

### Option B: Start Services Separately

**Terminal 1 - Backend:**
```bash
cd ai-service
python3.11 -m pip install -r requirements.txt  # First time only
python3.11 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install  # First time only
npm start
```

---

## ✅ Testing

Once everything is running:

### Health Check
```bash
curl http://localhost:8000/health
```

**Expected response:**
```json
{"status":"ok","service":"HireIQ API","version":"1.0.0"}
```

### Chat API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hi, I need help with my resume","session_id":"test-user-1"}'
```

**Expected response:**
```json
{
  "status": "success",
  "response": "I'd be happy to help with your resume!...",
  "session_id": "test-user-1"
}
```

### Open in Browser
- **Frontend:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

---

## 🔑 Configure GROQ API Key

1. Get your free API key: https://console.groq.com/
2. Edit `ai-service/.env`:
   ```
   GROQ_API_KEY=sk_live_xxxxxxxxxxxxx
   ```
3. Restart backend

---

## ⚠️ Troubleshooting

### "Port 8000/3000 already in use"
```bash
# Find what's using the port
lsof -i :8000  # For backend
lsof -i :3000  # For frontend

# Kill the process
kill -9 <PID>

# Or use the cleanup script
pkill -f uvicorn
pkill -f "npm start"
```

### "Module not found" errors
```bash
# Reinstall dependencies
cd ai-service
python3.11 -m pip install -r requirements.txt --force-reinstall
```

### Backend takes too long to start (first run)
This is **normal**! First startup loads ML models (~1-2 min). Subsequent starts are faster.

### Backend crashes with spaCy errors
Ignore these warnings - they don't affect functionality.

### CORS errors in browser
Make sure:
1. Backend is running on port 8000
2. Frontend is running on port 3000
3. Both are on `localhost` (not `127.0.0.1`)

---

## 📞 Support

**Quick Reference:**
- **Setup Checker:** `./check-setup.sh`
- **Logs:** `tail -f /tmp/hireiq-backend.log`
- **Stop All:** Press `Ctrl+C` in terminal running `./run-all.sh`
- **API Docs:** http://localhost:8000/docs (interactive Swagger UI)

---

## 🎉 You're Ready!

Once everything is running, you can:
- 💬 Chat with the AI
- 📄 Analyze resumes
- 🎯 Analyze job descriptions
- 📝 Generate cover letters
- 🎤 Practice interviews

Enjoy! 🚀

