from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from memory import get_history, add_message, clear_history, REDIS_AVAILABLE
from rag import answer_with_rag
from interview_bot import InterviewSession
from company_research import research_company
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse
from analytics import track_request, get_daily_stats, get_total_requests_today
from datetime import datetime
import psycopg2
import hashlib
import time
import os
import json
import re

PORT = int(os.getenv("PORT", 8000))

# LangSmith auto-traces all LangChain calls
# Just setting env vars is enough — no code changes needed!
os.environ["LANGCHAIN_TRACING_V2"]  = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_API_KEY"]     = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]     = os.getenv("LANGCHAIN_PROJECT", "hireiq")
os.environ["LANGCHAIN_ENDPOINT"]    = os.getenv("LANGCHAIN_ENDPOINT", "")

interview_sessions = {}

# Load API key
load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    print("⚠️  WARNING: GROQ_API_KEY not set. AI features will not work.")
    print("Set GROQ_API_KEY environment variable to enable LLM features.")
    client = None
else:
    client = Groq(api_key=groq_api_key)

# ── FASTAPI APP ───────────────────────────────────────────────
# This is like @SpringBootApplication in Java
app = FastAPI(
    title="HireIQ API",
    description="AI-powered job application assistant",
    version="1.0.0"
)

# Add CORS middleware after app is created
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://hireiq-frontend-ivory.vercel.app",  # your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_from_url():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        parsed = urlparse(database_url)
        return psycopg2.connect(
            dbname=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port
        )
    # Fallback to local
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "hireiq"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "root"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5432))
    )

# ── REQUEST MODELS ────────────────────────────────────────────
# Like @RequestBody DTOs in Spring Boot
# Java equivalent:
# public class ChatRequest {
#     private String message;
# }
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class JDRequest(BaseModel):
    job_description: str

class ResumeAnalysisRequest(BaseModel):
    resume: str
    job_description: str
    
class CoverLetterRequest(BaseModel):
    resume: str
    job_description: str
    company_name: str
    tone: str = "professional"  # default value — like Java optional param
    
class RAGRequest(BaseModel):
    question: str
    
class InterviewStartRequest(BaseModel):
    role: str
    difficulty: str = "medium"
    session_id: str

class InterviewAnswerRequest(BaseModel):
    session_id: str
    answer: str
    
class CompanyResearchRequest(BaseModel):
    company_name: str

# ── PROMPTS ───────────────────────────────────────────────────
JD_ANALYZER_PROMPT = """You are an expert job description analyzer.

TASK: Extract information from the job description provided by the user.

CRITICAL RULES:
1. You MUST extract real data from the job description — never return null
2. Return ONLY a valid JSON object — no text before or after
3. Do NOT explain anything — just return JSON

Return EXACTLY this JSON structure with real extracted values:
{
    "role": "exact job title from description",
    "company_type": "startup or enterprise or product-based or service-based",
    "required_skills": ["skill1", "skill2", "skill3"],
    "nice_to_have": ["skill1", "skill2"],
    "experience_years": "X+ years",
    "remote_friendly": true,
    "culture_signals": ["signal1", "signal2"],
    "salary_range": "range if mentioned or Not mentioned",
    "summary": "one sentence summary of the role"
}"""

RESUME_ANALYZER_PROMPT = """You are an expert resume analyzer and career coach.

TASK: Compare a resume against a job description and return a detailed analysis.

CRITICAL RULES:
1. Return ONLY valid JSON — no extra text
2. Be honest and specific in your analysis
3. match_score should be 0-100 based on how well resume matches JD
4. missing_skills = skills in JD but NOT in resume
5. matching_skills = skills in BOTH resume and JD
6. improvements = specific actionable suggestions

Return EXACTLY this JSON:
{
    "match_score": 85,
    "matching_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "strengths": ["strength1", "strength2"],
    "improvements": ["suggestion1", "suggestion2"],
    "summary": "overall assessment in one paragraph"
}"""

COVER_LETTER_PROMPT = """You are an expert cover letter writer.

TASK: Write a tailored, professional cover letter.

RULES:
1. Use the candidate's actual experience from their resume
2. Match the tone requested (professional/confident/friendly)
3. Highlight skills that match the job description
4. Keep it to 3 paragraphs — concise and impactful
5. Do NOT use generic phrases like "I am writing to express my interest"
6. Start with a strong, direct opening line
7. End with a confident call to action

Structure:
- Paragraph 1: Who you are + strongest relevant achievement
- Paragraph 2: Why you're perfect for THIS role at THIS company  
- Paragraph 3: Why you want THIS company + call to action"""

# ── HELPER FUNCTIONS ──────────────────────────────────────────
def call_llm(system_prompt, user_message, temperature=0.7):
    """
    Generic function to call Groq LLM.
    Java equivalent: a reusable service method
    """
    if not client:
        return {"error": "GROQ_API_KEY not configured. Please set environment variable."}
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        max_tokens=1024,
        temperature=temperature
    )
    return response.choices[0].message.content

def parse_json_response(raw_response):
    """
    Safely parse JSON from LLM response.
    Handles cases where AI adds extra text around JSON.
    """
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"error": "Could not parse response"}
    

def get_cache_key(text: str) -> str:
    """
    Generate cache key from text.
    Java equivalent: DigestUtils.md5Hex(text)
    """
    return hashlib.md5(text.lower().strip().encode()).hexdigest()

def get_cached_response(text: str) -> str:
    """Check Redis cache for existing response"""
    if not REDIS_AVAILABLE:
        return None
    try:
        from memory import r
        key = f"hireiq:cache:{get_cache_key(text)}"
        return r.get(key)
    except:
        return None

def cache_response(text: str, response: str, ttl: int = 3600):
    """Cache response for 1 hour"""
    if not REDIS_AVAILABLE:
        return
    try:
        from memory import r
        key = f"hireiq:cache:{get_cache_key(text)}"
        r.setex(key, ttl, response)
    except:
        pass

# ── API ENDPOINTS ─────────────────────────────────────────────

# Health check — like Spring Actuator /health
# Java: @GetMapping("/health")
@app.get("/health")
def health_check():
    """
    Simple health check for UptimeRobot monitoring.
    Returns 200 OK if service is up.
    """
    return {
        "status": "ok",
        "service": "HireIQ API",
        "version": "1.0.0"
    }

@app.get("/health/detailed")
def health_check_detailed():
    """
    Detailed health check with dependency status.
    For internal monitoring only.
    """
    health = {
        "status": "healthy",
        "service": "HireIQ API",
        "groq_configured": client is not None,
        "redis_available": REDIS_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    # Check database
    try:
        conn = get_db_from_url()
        conn.close()
        health["database_available"] = True
    except Exception as e:
        health["database_available"] = False
        health["status"] = "degraded"
        print(f"Database health check failed: {e}")
    
    return health

# Chat endpoint
# Java: @PostMapping("/api/chat")
@app.post("/api/chat")
def chat(request: ChatRequest):
    """Chat with persistent Redis memory"""
    start_time = time.time()  # Start timer
    # Get conversation history from Redis
    
    try:
        history = get_history(request.session_id)

        # Add user message to history
        add_message(request.session_id, "user", request.message)

        # Build messages for LLM — system + full history
        messages = [
            {
                "role": "system",
                "content": """You are HireIQ, an AI-powered job application 
                assistant. Help job seekers with resumes, interviews, and 
                career advice. Be friendly, direct, and specific."""
            },
            *history,  # Full conversation history from Redis
            {
                "role": "user",
                "content": request.message
            }
        ]

        # Call Groq with full history
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1024,
            temperature=0.7
        )

        ai_response = response.choices[0].message.content

        # Save AI response to Redis
        add_message(request.session_id, "assistant", ai_response)
        
        # Track successful request
        latency = (time.time() - start_time) * 1000
        track_request("chat", True, latency)

        return {
            "status": "success",
            "response": ai_response,
            "session_id": request.session_id
        }
    except Exception as e:
        # Track failed request
        latency = (time.time() - start_time) * 1000
        track_request("chat", False, latency)
        raise e

# Clear chat history endpoint
@app.delete("/api/chat/{session_id}")
def clear_chat(session_id: str):
    """Clear conversation history for a session"""
    clear_history(session_id)
    return {"status": "success", "message": "Chat history cleared"}

# JD Analyzer endpoint
# Java: @PostMapping("/api/analyze-jd")
@app.post("/api/analyze-jd")
def analyze_jd(request: JDRequest):
    """Analyze JD with caching"""
    start_time = time.time()

    # Check cache first
    cached = get_cached_response(request.job_description)
    if cached:
        track_request("jd_analyzer", True, 0)
        return {
            "status":   "success",
            "analysis": json.loads(cached),
            "cached":   True  # Tell frontend it was cached!
        }

    # Not cached — call LLM
    user_message = f"Extract all information:\n\n{request.job_description}"
    raw_response = call_llm(JD_ANALYZER_PROMPT, user_message, temperature=0.1)
    result       = parse_json_response(raw_response)

    # Cache for next time
    cache_response(request.job_description, json.dumps(result))

    latency = (time.time() - start_time) * 1000
    track_request("jd_analyzer", True, latency)

    return {
        "status":   "success",
        "analysis": result,
        "cached":   False
    }
    
# Resume Analyzer endpoint — NEW THIS WEEK! 🆕
# Java: @PostMapping("/api/analyze-resume")
@app.post("/api/analyze-resume")
def analyze_resume(request: ResumeAnalysisRequest):
    """
    Compare resume against job description.
    Returns match score, missing skills, and improvements.
    """
    
    user_message = f"""Compare this resume against the job description.

RESUME:
{request.resume}

JOB DESCRIPTION:
{request.job_description}

Return ONLY JSON with match score and analysis."""
    
    raw_response = call_llm(RESUME_ANALYZER_PROMPT, user_message, temperature=0.1)
    result = parse_json_response(raw_response)
    
    return {
        "status": "success",
        "analysis": result
    }
    
# Cover Letter Generator
# Java: @PostMapping("/api/cover-letter")
@app.post("/api/cover-letter")
def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate a tailored cover letter based on
    resume, job description, and company name.
    """
    
    user_message = f"""Write a cover letter for this candidate.

CANDIDATE RESUME:
{request.resume}

JOB DESCRIPTION:
{request.job_description}

COMPANY NAME: {request.company_name}

TONE: {request.tone}

Write a compelling, tailored cover letter that highlights 
the candidate's most relevant experience."""

    cover_letter = call_llm(
        COVER_LETTER_PROMPT,
        user_message,
        temperature=0.7  # slightly creative for natural writing
    )
    
    return {
        "status": "success",
        "cover_letter": cover_letter,
        "company": request.company_name
    }
    
    
    # RAG Question Answering — NEW! 🆕
@app.post("/api/ask")
def ask_knowledge_base(request: RAGRequest):
    """
    Answer career questions using RAG.
    Grounded in real documents — no hallucination!
    """
    result = answer_with_rag(request.question)
    return {
        "status":      "success",
        "answer":      result["answer"],
        "sources":     result["sources"],
        "chunks_used": result["chunks_used"]
    }
    
@app.post("/api/interview/start")
def start_interview(request: InterviewStartRequest):
    """Start a new interview session"""
    session = InterviewSession(request.role, request.difficulty)
    interview_sessions[request.session_id] = session
    question = session.generate_question()
    return {
        "status": "success",
        "question_number": 1,
        "total_questions": session.max_questions,
        "question": question
    }

@app.post("/api/interview/answer")
def submit_answer(request: InterviewAnswerRequest):
    """Submit answer and get feedback"""
    session = interview_sessions.get(request.session_id)
    if not session:
        return {"error": "Session not found"}

    evaluation = session.evaluate_answer(request.answer)

    if session.is_complete():
        final = session.generate_final_report()
        return {
            "status":    "completed",
            "evaluation": evaluation,
            "final_report": final
        }

    next_question = session.generate_question()
    return {
        "status":          "continue",
        "evaluation":      evaluation,
        "question_number": session.current_q + 1,
        "next_question":   next_question
    }
    
@app.post("/api/research-company")
def research_company_endpoint(request: CompanyResearchRequest):
    """AI agent researches a company autonomously"""
    result = research_company(request.company_name)
    return result

@app.get("/api/analytics")
def get_analytics():
    """
    Get usage analytics for today.
    Shows which features are most used.
    """
    stats = get_daily_stats()
    total = get_total_requests_today()

    return {
        "status":         "success",
        "today":          stats,
        "total_requests": total,
        "message":        "HireIQ Analytics Dashboard"
    }

@app.get("/api/analytics/{date}")
def get_analytics_by_date(date: str):
    """Get analytics for a specific date (YYYY-MM-DD)"""
    stats = get_daily_stats(date)
    return {"status": "success", "stats": stats}