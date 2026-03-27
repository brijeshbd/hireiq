from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os
import json
import re

# Load API key
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── FASTAPI APP ───────────────────────────────────────────────
# This is like @SpringBootApplication in Java
app = FastAPI(
    title="HireIQ API",
    description="AI-powered job application assistant",
    version="1.0.0"
)

# ── REQUEST MODELS ────────────────────────────────────────────
# Like @RequestBody DTOs in Spring Boot
# Java equivalent:
# public class ChatRequest {
#     private String message;
# }
class ChatRequest(BaseModel):
    message: str

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

# ── API ENDPOINTS ─────────────────────────────────────────────

# Health check — like Spring Actuator /health
# Java: @GetMapping("/health")
@app.get("/health")
def health_check():
    return {"status": "HireIQ is running! 🤖"}

# Chat endpoint
# Java: @PostMapping("/api/chat")
@app.post("/api/chat")
def chat(request: ChatRequest):
    """Simple chat with HireIQ"""
    
    system_prompt = """You are HireIQ, an AI-powered job application 
    assistant. Help job seekers with resumes, interviews, and career advice.
    Be friendly, direct, and give specific actionable advice."""
    
    response = call_llm(system_prompt, request.message, temperature=0.7)
    
    # Java equivalent: return ResponseEntity.ok(new ChatResponse(response))
    return {
        "status": "success",
        "response": response
    }

# JD Analyzer endpoint
# Java: @PostMapping("/api/analyze-jd")
@app.post("/api/analyze-jd")
def analyze_jd(request: JDRequest):
    """Analyze a job description and extract structured data"""
    
    user_message = f"Extract all information from this job description:\n\n{request.job_description}\n\nReturn ONLY JSON."
    
    raw_response = call_llm(JD_ANALYZER_PROMPT, user_message, temperature=0.1)
    result = parse_json_response(raw_response)
    
    return {
        "status": "success",
        "analysis": result
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