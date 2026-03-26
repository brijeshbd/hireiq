from groq import Groq
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def ask_hireiq(user_message):
    """Send a message to Groq LLM and get a response"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Free, fast, powerful model
        messages=[
            {
                "role": "system",
                "content": "You are HireIQ, an AI-powered job application assistant. "
                           "You help job seekers write better resumes, prepare for "
                           "interviews, and find their dream remote jobs."
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        max_tokens=1024,
        temperature=0.7
    )
    
    return response.choices[0].message.content

# Test it!
if __name__ == "__main__":
    print("🤖 HireIQ is starting...\n")
    print("=" * 50)
    
    # Test 1 — General question
    print("\n📌 Test 1:")
    question1 = "What skills should a Java backend engineer learn in 2026?"
    print(f"You: {question1}\n")
    response1 = ask_hireiq(question1)
    print(f"HireIQ: {response1}")
    
    print("\n" + "=" * 50)
    
    # Test 2 — Your personal situation
    print("\n📌 Test 2:")
    question2 = (
        "I have 3 years of Java Spring Boot experience across "
        "Fintech, MarTech and SaaS companies. I want a remote job "
        "in the US or Japan. What should I focus on?"
    )
    print(f"You: {question2}\n")
    response2 = ask_hireiq(question2)
    print(f"HireIQ: {response2}")
    
    print("\n" + "=" * 50)
    print("\n✅ HireIQ is working! Week 1 done 🎉")