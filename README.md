# 🤖 HireIQ - Your AI-Powered Job Application Assistant

## What is HireIQ? (In Simple Words)

**Think of HireIQ as your personal job search coach powered by AI.**

Imagine you're applying for a job and you have these questions:
- "Does my resume match this job description?"
- "What skills should I focus on for this company?"
- "How do I write a great cover letter?"
- "Can I practice for the interview?"

**HireIQ answers all these questions automatically using Artificial Intelligence (AI).** It's like having a career expert available 24/7 to help you prepare for your dream job.

---

## 🎯 What Can HireIQ Do?

### 1. **💬 Chat with AI**
- Ask HireIQ anything about job searching, interviews, resumes, or career advice
- Get instant, personalized responses
- Have a real conversation (not just keyword matching)

### 2. **📄 Resume Analyzer**
- Paste your resume and a job description
- Get a **match score** (e.g., "78% match")
- See which of your skills match the job
- Get tips on what to improve

### 3. **🔍 Job Description Analyzer**
- Paste any job posting
- HireIQ extracts and explains:
  - Required skills
  - Experience level
  - Company culture signals
  - Salary range

### 4. **✍️ Cover Letter Generator**
- Tell HireIQ about yourself, the job, and company
- Get a **custom cover letter** written specifically for that job
- Choose the tone: professional, confident, or friendly

### 5. **🎤 Mock Interview**
- Practice technical interview questions
- Choose difficulty level (easy, medium, hard)
- Get scored on your answers (0-100)
- Receive feedback and improvement tips

---

## 🏗️ How Does HireIQ Work? (The Magic Behind The Scenes)

### The 3-Layer Architecture

HireIQ works like a sandwich with 3 layers:

```
┌─────────────────────────────────────────┐
│  FRONTEND (React - What you see)        │  ← Beautiful, interactive buttons & forms
│  💻 Web interface - User clicks here    │
└─────────────────────────────────────────┘
                    ↓ (sends requests)
┌─────────────────────────────────────────┐
│  API (FastAPI - The middleman)          │  ← Routes requests to the right place
│  🌉 Receives requests & sends responses │
└─────────────────────────────────────────┘
                    ↓ (processes)
┌─────────────────────────────────────────┐
│  AI SERVICE (Python - The Brain)        │  ← Uses LLMs to generate smart responses
│  🧠 Does the actual AI thinking         │
└─────────────────────────────────────────┘
```

### Technology Stack (What Powers Each Layer)

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React (JavaScript) | Interactive web interface |
| **API** | FastAPI (Python) | Receives requests, routes to AI |
| **AI** | Groq LLM + LangChain | Generates intelligent responses |
| **Storage** | Redis + PostgreSQL | Remembers conversations & embeddings |

### Why This Architecture?

- **Separation of concerns**: Each layer does one job well
- **Scalability**: Can upgrade each layer independently
- **Maintainability**: Easy to understand and modify
- **Flexibility**: Can use HireIQ on web, mobile, API, etc.

---

## 🚀 Installation Guide (Step by Step)

### Prerequisites
**What you need before starting:**

- **Git**: Version control (used to download the code)
  - macOS: Already installed
  - Windows: Download from https://git-scm.com/
  - Linux: `sudo apt install git`

- **Python 3.11+**: Programming language
  - macOS: `brew install python@3.11`
  - Windows: Download from https://www.python.org/
  - Linux: `sudo apt install python3.11`

- **Node.js (v18+)**: Required for React frontend
  - macOS: `brew install node`
  - Windows/Linux: Download from https://nodejs.org/

- **PostgreSQL**: Database (stores job data with AI embeddings)
  - macOS: `brew install postgresql`
  - Windows: Download from https://www.postgresql.org/
  - Linux: `sudo apt install postgresql`

- **Redis**: In-memory cache (stores chat history)
  - macOS: `brew install redis`
  - Windows: Use Docker or WSL
  - Linux: `sudo apt install redis-server`

- **Groq API Key**: Free AI access
  - Get it at https://console.groq.com/ (sign up → API keys → copy)

### Step 1: Download HireIQ

```bash
# Clone the repository
git clone https://github.com/brijeshbd/hireiq.git
cd hireiq
```

**What happened?** Git downloaded all the code files to your computer.

### Step 2: Setup the AI Service (Backend)

```bash
cd ai-service

# Create a virtual environment (isolated Python space)
python3.11 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_api_key_here" > .env
echo "REDIS_HOST=localhost" >> .env
echo "REDIS_PORT=6379" >> .env
```

**What happened?** 
- Created a sandbox for Python packages (venv)
- Installed all required Python libraries
- Set up environment variables (API keys)

### Step 3: Start Redis (Conversation Memory)

```bash
# In a new terminal
redis-server

# You should see: "Ready to accept connections"
```

**What happened?** Redis started and is now storing chat history in memory.

### Step 4: Start the AI Service

```bash
# From ai-service directory (with venv activated)
uvicorn api:app --reload --port 8000

# You should see: "Uvicorn running on http://127.0.0.1:8000"
```

**What happened?** The FastAPI server started and is listening for requests on port 8000.

### Step 5: Setup the Frontend (React)

```bash
# In a new terminal, go to frontend folder
cd hireiq/frontend

# Install dependencies
npm install

# Start the development server
npm start

# Browser should open at http://localhost:3000
```

**What happened?** React bundled all code and started a dev server.

---

## 📚 Project Structure (File Organization)

```
hireiq/
│
├── frontend/                          # 💻 What users see (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.js               # Chat interface
│   │   │   ├── ResumeAnalyzer.js     # Resume matching
│   │   │   ├── JDAnalyzer.js         # Job description parsing
│   │   │   ├── CoverLetter.js        # Cover letter generation
│   │   │   └── Interview.js          # Mock interview
│   │   ├── App.js                    # Main app layout
│   │   └── App.css                   # Styling
│   └── package.json                  # Node dependencies
│
├── ai-service/                        # 🧠 The AI brain (Python)
│   ├── api.py                        # FastAPI endpoints
│   ├── jd_analyzer.py                # Job description analyzer
│   ├── memory.py                     # Redis conversation storage
│   ├── main.py                       # Main entry point
│   ├── requirements.txt              # Python dependencies
│   └── .env                          # Environment variables (API keys)
│
├── backend/                           # ☕ Java service (optional)
│   └── src/                          # Spring Boot application
│
└── README.md                          # This file!
```

---

## 🔌 How the Pieces Connect

### User Flow Example: "Analyze My Resume"

```
1. User clicks "Resume Analyzer" button in React app
                ↓
2. User pastes resume + job description + clicks "Analyze"
                ↓
3. React sends data to: POST http://localhost:8000/api/analyze-resume
                ↓
4. FastAPI receives request, calls jd_analyzer.py
                ↓
5. jd_analyzer.py sends text to Groq LLM (AI in the cloud)
                ↓
6. Groq LLM analyzes and returns: {"match_score": 78, "skills": [...], "feedback": "..."}
                ↓
7. FastAPI sends response back to React
                ↓
8. React displays results to user: "78% Match! ✅"
```

---

## 🤖 What is "AI" and How Does HireIQ Use It?

### The Simple Explanation

**AI (Artificial Intelligence)** is software that can understand language and give intelligent responses, similar to how humans think.

HireIQ uses **Groq LLM (Large Language Model)**, which is like asking ChatGPT questions:

```
You ask:    "Does this resume match the job description?"
             ↓
LLM reads both texts and understands them
             ↓
LLM thinks and composes a response
             ↓
You get:    "Yes, 78% match. Your Java skills are great, 
             but you need more cloud experience."
```

### Key AI Concepts in HireIQ

| Concept | What It Does | Example |
|---------|-------------|---------|
| **LLM** | Understands and generates text | ChatGPT, Groq |
| **Embeddings** | Converts text to numbers for comparison | "Java backend" → [0.2, 0.8, 0.1, ...] |
| **Vector Search** | Finds similar jobs by comparing embeddings | Find jobs similar to "Java Spring Boot" |
| **Prompt Engineering** | Writing instructions for AI to follow | "Analyze this resume and give match score" |
| **Memory** | Stores conversation history | Redis remembers what you said earlier |

---

## 🔧 Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'langchain'"

**Cause:** Dependencies not installed.

**Solution:**
```bash
cd ai-service
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Cannot connect to Redis"

**Cause:** Redis server not running.

**Solution:**
```bash
# Terminal 1
redis-server

# Terminal 2 - then run your app
uvicorn api:app --reload --port 8000
```

### Issue: "GROQ_API_KEY not set"

**Cause:** Missing environment variable.

**Solution:**
```bash
# In ai-service directory
echo "GROQ_API_KEY=sk_live_your_key_here" > .env

# Get your key from https://console.groq.com/
```

### Issue: "npm: command not found"

**Cause:** Node.js not installed.

**Solution:**
```bash
# macOS
brew install node

# Verify
node --version
npm --version
```

---

## 📖 Detailed Explanations

### Why PostgreSQL + pgvector?

**PostgreSQL** = Main database (stores job listings)
**pgvector** = Extension for AI embeddings (finds similar jobs)

**Analogy:** If PostgreSQL is a library, pgvector adds a "similarity search" feature so you can find books similar to one you like.

### Why Redis?

**Purpose:** Store chat history in memory (super fast)

**Why not just use database?**
- Database is slower (disk access)
- Chat needs to be fast (user expects instant responses)
- Redis forgets data when restarted (that's okay for temporary chat)

**Analogy:** Database = book library (permanent, but slow to search). Redis = your notebook (temporary, but quick to flip through).

### Why LangChain?

**LangChain** is a framework that makes AI easier to use:
- Chains LLM calls together
- Manages prompts
- Handles memory
- Connects tools (like calculators, web search)

**Analogy:** Like a recipe book for AI - instead of coding AI from scratch, you use pre-made recipes.

---

## 🚀 Next Steps After Installation

### 1. **Test the API**
```bash
curl http://localhost:8000/health
# Response: {"status": "HireIQ is running! 🤖"}
```

### 2. **Test Resume Analysis**
```bash
curl -X POST http://localhost:8000/api/analyze-resume \
  -H "Content-Type: application/json" \
  -d '{
    "resume": "5 years Java Spring Boot experience",
    "job_description": "Need 3+ years Java backend engineer"
  }'
```

### 3. **Try the Frontend**
- Open http://localhost:3000 in your browser
- Try each tab: Chat, Resume Analyzer, etc.

---

## 🛠️ Development Tips

### Running Everything at Once (Recommended)

Create a shell script `run.sh`:

```bash
#!/bin/bash

# Terminal 1: Redis
redis-server &

# Terminal 2: AI Service
cd ai-service
source venv/bin/activate
uvicorn api:app --reload --port 8000 &

# Terminal 3: Frontend
cd frontend
npm start &

echo "✅ All services running!"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8000"
```

```bash
chmod +x run.sh
./run.sh
```

### Debugging

**View API logs:**
```bash
# Terminal running uvicorn will show logs
# Look for: POST /api/analyze-resume - successful request logs
```

**Check if Redis is working:**
```bash
redis-cli ping
# Response: PONG
```

**Check if services are running:**
```bash
lsof -i :8000   # Check AI service port
lsof -i :3000   # Check frontend port
lsof -i :6379   # Check Redis port
```

---

## 🎓 Learning Resources

### To Understand More:

1. **React** (Frontend):
   - Official: https://react.dev/
   - Beginner tutorial: 30 min introduction

2. **FastAPI** (API):
   - Official: https://fastapi.tiangolo.com/
   - Why: Fastest Python web framework

3. **LLMs & AI**:
   - https://www.deeplearning.ai/short-courses/
   - Start with: "ChatGPT Prompt Engineering for Developers"

4. **Vector Databases**:
   - Concept: https://www.youtube.com/watch?v=dN0lsF2cvm4
   - pgvector docs: https://github.com/pgvector/pgvector

---

## 🤝 Contributing

Want to improve HireIQ? Here's how:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test locally
4. Commit: `git commit -m "Add amazing feature"`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

---

## 📝 License

This project is open source. Feel free to use it for learning and development.

---

## ❓ FAQ

**Q: Do I need to know coding to use HireIQ?**
A: No! You just need to follow the installation steps. The UI is user-friendly.

**Q: Is my data safe?**
A: Your data stays on your computer. We don't send anything to external servers except AI requests to Groq (which has privacy standards).

**Q: Can I use HireIQ without an internet connection?**
A: No, because Groq LLM (AI) runs in the cloud. But all your data is processed locally first.

**Q: How much does it cost?**
A: Groq offers free tier. Check their pricing at https://console.groq.com/

**Q: Can I deploy HireIQ to the internet?**
A: Yes! You can deploy frontend to Vercel, API to Railway, and database to a managed cloud provider. Ask for deployment guide.

---

## 📞 Support

- **Found a bug?** Open an issue on GitHub
- **Have a question?** Create a discussion
- **Want to chat?** Reach out to the creator

---

## 🙏 Acknowledgments

- **Groq** - For providing fast, free AI inference
- **LangChain** - For making AI integration easy
- **React & FastAPI communities** - For excellent frameworks

---

**Happy job hunting! 🎯 May HireIQ help you land your dream job! 🚀**