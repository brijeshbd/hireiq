from langchain_groq import ChatGroq
# langchain v1+ splits some APIs into `langchain_core` package. Import
# prompt and output-parser classes from langchain_core so imports work
# with the installed packages in this venv.
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from dotenv import load_dotenv
import os
import json

load_dotenv()

# ── SETUP ─────────────────────────────────────────────────────
# LangChain Groq client
# Java equivalent: new LangChainClient(apiKey, model)
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)

# ── PROMPT TEMPLATES ──────────────────────────────────────────
# LangChain PromptTemplate — like a Java String.format() on steroids
# Variables in {} get filled in when chain runs

QUESTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical interviewer for {role} positions.
    
Generate ONE interview question based on:
- Role: {role}
- Difficulty: {difficulty}  
- Topic: {topic}
- Questions asked so far: {questions_asked}

RULES:
1. Ask only ONE question
2. Make it specific and technical
3. Don't repeat previous questions
4. Match the difficulty level
5. Return ONLY the question — no explanation"""),
    ("human", "Generate the next interview question.")
])

EVALUATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical interviewer evaluating answers.

Role being interviewed for: {role}
Question asked: {question}
Candidate's answer: {answer}

Evaluate the answer and return ONLY valid JSON:
{{
    "score": 85,
    "score_label": "Good",
    "key_points_covered": ["point1", "point2"],
    "missing_points": ["point1", "point2"],
    "feedback": "specific constructive feedback",
    "ideal_answer_hint": "what a perfect answer would include"
}}

Score guide:
- 90-100: Excellent — covered all key points with depth
- 70-89:  Good — covered main points, missed some details  
- 50-69:  Average — partial understanding shown
- 0-49:   Needs work — significant gaps in knowledge"""),
    ("human", "Evaluate this answer.")
])

FINAL_REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert career coach giving interview feedback.

Candidate interviewed for: {role}
Interview results: {results}

Write a comprehensive final report with:
1. Overall performance summary
2. Top 3 strengths demonstrated
3. Top 3 areas to improve
4. Specific resources to study
5. Readiness verdict: Ready / Almost Ready / Needs More Prep

Be honest, specific, and encouraging."""),
    ("human", "Generate the final interview report.")
])

# ── CHAINS ────────────────────────────────────────────────────
# LangChain chains — connect prompt + llm + output parser
# Java equivalent: prompt.apply(vars) | llm.call() | parser.parse()

# StrOutputParser just returns the text response as a string
question_chain = QUESTION_PROMPT | llm | StrOutputParser()
report_chain   = FINAL_REPORT_PROMPT | llm | StrOutputParser()

# ── INTERVIEW SESSION ─────────────────────────────────────────

class InterviewSession:
    """
    Manages a complete interview session.
    Java equivalent: public class InterviewSession { ... }
    """

    def __init__(self, role: str, difficulty: str = "medium"):
        self.role        = role
        self.difficulty  = difficulty
        self.questions   = []    # Questions asked so far
        self.answers     = []    # Candidate's answers
        self.evaluations = []    # Evaluation for each answer
        self.current_q   = 0    # Current question number
        self.max_questions = 5  # Total questions per interview

        # Topics to cover for backend engineer
        self.topics = [
            "Java and Spring Boot fundamentals",
            "Microservices and distributed systems",
            "Database design and optimization",
            "System design and scalability",
            "Problem solving and past experience"
        ]

    def generate_question(self) -> str:
        """Generate next interview question using LangChain"""

        topic = self.topics[self.current_q % len(self.topics)]

        # Run the question chain
        # Java equivalent: questionChain.invoke(variables)
        question = question_chain.invoke({
            "role":            self.role,
            "difficulty":      self.difficulty,
            "topic":           topic,
            "questions_asked": str(self.questions) if self.questions else "None yet"
        })

        self.questions.append(question)
        return question

    def evaluate_answer(self, answer: str) -> dict:
        """Evaluate candidate's answer using LangChain"""

        self.answers.append(answer)

        # Get current question
        current_question = self.questions[self.current_q]

        # Run evaluation chain
        # Note: We call llm directly here to parse JSON
        eval_prompt = EVALUATION_PROMPT.format_messages(
            role=self.role,
            question=current_question,
            answer=answer
        )

        raw_response = llm.invoke(eval_prompt).content

        # Parse JSON response
        try:
            evaluation = json.loads(raw_response)
        except json.JSONDecodeError:
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
            else:
                evaluation = {
                    "score": 70,
                    "score_label": "Good",
                    "feedback": raw_response,
                    "missing_points": [],
                    "key_points_covered": [],
                    "ideal_answer_hint": ""
                }

        self.evaluations.append(evaluation)
        self.current_q += 1
        return evaluation

    def is_complete(self) -> bool:
        """Check if interview is done"""
        return self.current_q >= self.max_questions

    def generate_final_report(self) -> str:
        """Generate comprehensive final report"""

        # Build results summary
        results = []
        for i, (q, a, e) in enumerate(
            zip(self.questions, self.answers, self.evaluations)
        ):
            results.append({
                "question_number": i + 1,
                "question":   q,
                "answer":     a[:200] + "..." if len(a) > 200 else a,
                "score":      e.get("score", 0),
                "feedback":   e.get("feedback", "")
            })

        avg_score = sum(
            e.get("score", 0) for e in self.evaluations
        ) / len(self.evaluations)

        report = report_chain.invoke({
            "role":    self.role,
            "results": json.dumps(results, indent=2)
        })

        return {
            "report":    report,
            "avg_score": round(avg_score, 1),
            "total_questions": len(self.questions)
        }

    def get_score_emoji(self, score: int) -> str:
        if score >= 90: return "🌟"
        if score >= 70: return "✅"
        if score >= 50: return "⚠️"
        return "❌"


# ── INTERACTIVE TERMINAL INTERVIEW ────────────────────────────

def run_interview():
    """Run a complete mock interview in terminal"""

    print("\n" + "="*55)
    print("🎤 HIREIQ MOCK INTERVIEW")
    print("="*55)

    # Get role from user
    print("\nAvailable roles:")
    print("1. Java Backend Engineer")
    print("2. Senior Software Engineer")
    print("3. LLM Engineer")
    role_choice = input("\nEnter role (or type your own): ").strip()

    if role_choice == "1":
        role = "Java Backend Engineer"
    elif role_choice == "2":
        role = "Senior Software Engineer"
    elif role_choice == "3":
        role = "LLM Engineer"
    else:
        role = role_choice

    # Get difficulty
    print("\nDifficulty: easy / medium / hard")
    difficulty = input("Choose difficulty (default: medium): ").strip()
    if difficulty not in ["easy", "medium", "hard"]:
        difficulty = "medium"

    print(f"\n🚀 Starting {difficulty} interview for: {role}")
    print("💡 Tip: Answer as you would in a real interview")
    print("="*55)

    # Create session
    session = InterviewSession(role, difficulty)

    # Run interview loop
    while not session.is_complete():
        q_num = session.current_q + 1
        print(f"\n📌 Question {q_num} of {session.max_questions}")
        print("-"*40)

        # Generate question
        print("⏳ Generating question...")
        question = session.generate_question()
        print(f"\n❓ {question}")
        print()

        # Get answer
        print("Your answer (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        answer = "\n".join(lines[:-1])

        if not answer.strip():
            answer = "I'm not sure about this one."

        # Evaluate answer
        print("\n⏳ Evaluating your answer...")
        evaluation = session.evaluate_answer(answer)

        # Show feedback
        score = evaluation.get("score", 0)
        emoji = session.get_score_emoji(score)

        print(f"\n{emoji} Score: {score}/100 — {evaluation.get('score_label', '')}")
        print(f"\n💬 Feedback: {evaluation.get('feedback', '')}")

        if evaluation.get("missing_points"):
            print(f"\n📝 You could have mentioned:")
            for point in evaluation.get("missing_points", []):
                print(f"   • {point}")

        if evaluation.get("ideal_answer_hint"):
            print(f"\n💡 Hint: {evaluation.get('ideal_answer_hint', '')}")

        print("\n" + "="*55)

    # Generate final report
    print("\n⏳ Generating your final interview report...")
    final = session.generate_final_report()

    print("\n" + "="*55)
    print("📊 FINAL INTERVIEW REPORT")
    print("="*55)
    print(f"\n🎯 Average Score: {final['avg_score']}/100")
    print(f"\n{final['report']}")
    print("\n" + "="*55)
    print("✅ Interview complete! Good luck Brijesh! 💪")


# ── RUN ───────────────────────────────────────────────────────
if __name__ == "__main__":
    run_interview()