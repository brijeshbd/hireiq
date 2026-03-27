from groq import Groq
from dotenv import load_dotenv
import os
import json

# Load API key
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── PROMPT ENGINEERING ────────────────────────────────────────
# This is the key — very specific instructions
# Tell AI exactly what to do and what format to return
JD_ANALYZER_PROMPT = """You are an expert job description analyzer.

TASK: Extract information from the job description provided by the user.

CRITICAL RULES:
1. You MUST extract real data from the job description — never return null
2. Return ONLY a valid JSON object — no text before or after
3. Do NOT explain anything — just return JSON
4. Read the ENTIRE job description carefully before responding

Return EXACTLY this JSON structure with real extracted values:
{
    "role": "exact job title from description",
    "company_type": "startup or enterprise or product-based or service-based",
    "required_skills": ["skill1", "skill2", "skill3"],
    "nice_to_have": ["skill1", "skill2"],
    "experience_years": "X+ years",
    "remote_friendly": true,
    "culture_signals": ["signal1", "signal2"],
    "salary_range": "range if mentioned",
    "summary": "one sentence summary of the role"
}

REMEMBER: Extract from the actual job description. Never return null values."""


def analyze_job_description(job_description):
    """
    Analyze a job description and return structured JSON.
    
    This function uses prompt engineering to:
    1. Force the AI to return only JSON (no extra text)
    2. Define exactly what fields we want
    3. Handle missing information gracefully
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": JD_ANALYZER_PROMPT  # ← Our engineered prompt
            },
            {
                "role": "user",
                "content": f"Extract all information from this job description and return as JSON:\n\n{job_description}\n\nRemember: Return ONLY JSON with real extracted values."
            }
        ],
        max_tokens=1024,
        temperature=0.1  # ← Low temperature = consistent, predictable output
                         # We don't want creativity here — we want accuracy!
    )
    
    # Get raw response text
    raw_response = response.choices[0].message.content
    
    # Parse JSON — convert text to Python dictionary
    # Java equivalent: objectMapper.readValue(rawResponse, Map.class)
    try:
        result = json.loads(raw_response)
        return result
    except json.JSONDecodeError:
        # Sometimes AI adds extra text — try to find JSON in response
        import re
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            return {"error": "Could not parse response", "raw": raw_response}


def print_analysis(analysis):
    """Pretty print the job analysis results"""
    
    print("\n" + "="*50)
    print("📊 JOB DESCRIPTION ANALYSIS")
    print("="*50)
    
    if "error" in analysis:
        print(f"❌ Error: {analysis['error']}")
        return
    
    print(f"\n🎯 Role:          {analysis.get('role') or 'N/A'}")
    print(f"🏢 Company Type:  {analysis.get('company_type') or 'N/A'}")
    print(f"📅 Experience:    {analysis.get('experience_years') or 'N/A'}")
    print(f"🌍 Remote:        {analysis.get('remote_friendly') or 'N/A'}")
    print(f"💰 Salary:        {analysis.get('salary_range') or 'N/A'}")
    
    print(f"\n✅ Required Skills:")
    for skill in analysis.get('required_skills') or []:
        print(f"   • {skill}")
    
    print(f"\n⭐ Nice to Have:")
    for skill in analysis.get('nice_to_have') or []:
        print(f"   • {skill}")
    
    print(f"\n🎭 Culture Signals:")
    for signal in analysis.get('culture_signals') or []:
        print(f"   • {signal}")
    
    print(f"\n📝 Summary: {analysis.get('summary') or 'N/A'}")
    print("="*50)


# ── TEST IT ───────────────────────────────────────────────────
if __name__ == "__main__":
    
    # Sample job description — similar to ones you'd apply for!
    sample_jd = """
    Senior Backend Engineer — Remote (US/Japan)
    
    We are a fast-growing fintech startup looking for a Senior Backend 
    Engineer to join our distributed team. You will own and build 
    core payment processing microservices.
    
    Requirements:
    - 3+ years of backend engineering experience
    - Strong expertise in Java and Spring Boot
    - Experience with Apache Kafka and event-driven architecture
    - PostgreSQL and database optimization
    - AWS (EC2, S3, SQS)
    - Docker and Kubernetes
    
    Nice to have:
    - Experience with Python
    - Knowledge of AI/LLM integration
    - Go programming language
    
    We offer:
    - Fully remote position
    - Competitive salary $80,000 - $120,000
    - Async-first culture
    - Strong ownership and autonomy
    - Fast-paced startup environment
    """
    
    print("🔍 Analyzing job description...")
    
    # Analyze it
    result = analyze_job_description(sample_jd)
    
    # Print nicely
    print_analysis(result)
    
    # Also print raw JSON
    print("\n📄 Raw JSON Output:")
    print(json.dumps(result, indent=2))