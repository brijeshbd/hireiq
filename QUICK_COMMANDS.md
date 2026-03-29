# Quick Commands for HireIQ Development

## One-Liners

### 🚀 Start Everything
```bash
cd ~/Documents/projects/python/hireiq && ./run-all.sh
```

### 🔙 Start Only Backend
```bash
cd ~/Documents/projects/python/hireiq/ai-service && python3.11 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

### 💻 Start Only Frontend
```bash
cd ~/Documents/projects/python/hireiq/frontend && npm start
```

### 📦 Install Dependencies (Python 3.11 required)
```bash
cd ~/Documents/projects/python/hireiq/ai-service && python3.11 -m pip install -r requirements.txt
```

### 🧪 Test API
```bash
curl -X POST http://localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello","session_id":"test"}'
```

### 📚 View API Docs
```bash
open http://localhost:8000/docs
```

### ✅ Check Health
```bash
curl http://localhost:8000/health | jq .
```

## Shell Aliases (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# HireIQ shortcuts
alias hireiq-start='cd ~/Documents/projects/python/hireiq && ./run-all.sh'
alias hireiq-backend='cd ~/Documents/projects/python/hireiq/ai-service && python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload'
alias hireiq-frontend='cd ~/Documents/projects/python/hireiq/frontend && npm start'
alias hireiq-test='curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\":\"Hi\",\"session_id\":\"test\"}" | jq .'
alias hireiq-logs='tail -f /tmp/hireiq-logs/*.log'
```

Then reload: `source ~/.zshrc`

Now you can just run:
```bash
hireiq-start      # Start everything
hireiq-backend    # Just backend
hireiq-frontend   # Just frontend
hireiq-test       # Test API
```

