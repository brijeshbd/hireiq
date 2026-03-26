from groq import Groq
from dotenv import load_dotenv
import os

# Load API key from .env file
load_dotenv()

# Create Groq client
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ── CONVERSATION MEMORY ──────────────────────────────────────
# This list stores the entire conversation history
# Think of it like an ArrayList<Message> in Java
conversation_history = []

# System prompt — HireIQ's personality and rules
SYSTEM_PROMPT = """You are HireIQ, an AI-powered job application assistant.
You help job seekers with:
- Resume analysis and improvement
- Cover letter generation  
- Interview preparation
- Job search strategy
- Career advice

You are friendly, direct, and give specific actionable advice.
You remember everything the user tells you in this conversation."""



def ask_hireiq(user_message):
    """Send a message to Groq LLM and get a response"""
    
    conversation_history.append({"role": "user", "content": user_message})
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Free, fast, powerful model
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            *conversation_history,  # Include entire conversation history
        ],
        max_tokens=1024,
        temperature=0.7
    )
    
    ai_response = response.choices[0].message.content
    
    conversation_history.append({"role": "assistant", "content": ai_response})
    
    return ai_response

def chat():
    """Interactive chat loop — talk to HireIQ in terminal.
    Like a while(true) loop in Java waiting for user input.
    """
    print("=" * 50)
    print("🤖 Welcome to HireIQ!")
    print("💡 Type 'quit' to exit")
    print("💡 Type 'history' to see conversation")
    print("=" * 50)
    print()
    
    # Keep chatting until user types 'quit'
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() == "quit":
            print("👋 Goodbye! Good luck with your job search!!")
            break
        elif user_input.lower() == "history":
            print("\n📜 Conversation History:")
            for msg in conversation_history:
                role = "You" if msg["role"] == "user" else "HireIQ"
                print(f"{role}: {msg['content'][:80]}...")
            print()
            continue
        
       # Skip empty input
        if not user_input:
            continue
        
        # Get response from HireIQ
        print("\nHireIQ: ", end="", flush=True)
        response = ask_hireiq(user_input)
        print(response)
        print()


# Test it!
if __name__ == "__main__":
    chat()