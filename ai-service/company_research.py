from langchain_groq import ChatGroq
# AgentExecutor and create_react_agent now live in `langchain_classic`
# in the installed environment. Use the classic package to access
# the AgentExecutor implementation.
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import Tool
# Prompt templates live under langchain_core in this setup
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from dotenv import load_dotenv
import os
import json
import requests
from bs4 import BeautifulSoup

load_dotenv()

# ── SETUP ─────────────────────────────────────────────────────
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile",
    temperature=0.3
)

# ── TOOLS ─────────────────────────────────────────────────────
# Tools are functions the agent can CHOOSE to call
# Java equivalent: List<Tool> tools = new ArrayList<>();

# Tool 1 — Wikipedia Search
wikipedia = WikipediaAPIWrapper(top_k_results=2)
wikipedia_tool = WikipediaQueryRun(api_wrapper=wikipedia)

# Tool 2 — Company Tech Stack Analyzer
def analyze_company_tech(company_name: str) -> str:
    """
    Analyze what tech stack a company likely uses
    based on their known engineering culture.
    """
    known_stacks = {
        "mercari": {
            "backend": ["Go", "Java", "Kotlin", "Spring Boot"],
            "infra":   ["Kubernetes", "GCP", "Spinnaker"],
            "data":    ["BigQuery", "Dataflow"],
            "culture": "English-first, microservices, high autonomy"
        },
        "rakuten": {
            "backend": ["Java", "Spring Boot", "PHP"],
            "infra":   ["AWS", "Docker", "Kubernetes"],
            "data":    ["Hadoop", "Spark"],
            "culture": "Large enterprise, diverse teams, Java heavy"
        },
        "line": {
            "backend": ["Java", "Spring Boot", "Go", "Python"],
            "infra":   ["Kubernetes", "Kafka", "AWS"],
            "data":    ["Flink", "Kafka Streams"],
            "culture": "Engineering driven, open source friendly"
        },
        "paypay": {
            "backend": ["Java", "Spring Boot", "Kotlin"],
            "infra":   ["AWS", "Kubernetes", "Kafka"],
            "data":    ["PostgreSQL", "Redis"],
            "culture": "Fintech, fast-paced, high scale"
        },
        "atlassian": {
            "backend": ["Java", "Python", "Go"],
            "infra":   ["AWS", "Kubernetes", "Terraform"],
            "data":    ["PostgreSQL", "DynamoDB"],
            "culture": "Distributed-first, async, remote-friendly"
        },
        "razorpay": {
            "backend": ["Go", "Java", "Python"],
            "infra":   ["AWS", "Kubernetes", "Kafka"],
            "data":    ["MySQL", "Redis", "Elasticsearch"],
            "culture": "Fintech startup, high ownership, fast growth"
        }
    }

    # Check if we know this company
    key = company_name.lower().replace(" ", "")
    for known_key, stack in known_stacks.items():
        if known_key in key:
            return json.dumps({
                "company": company_name,
                "tech_stack": stack,
                "found": True
            }, indent=2)

    return json.dumps({
        "company": company_name,
        "message": "Detailed tech stack not in database. Using Wikipedia and general knowledge.",
        "found": False
    })

# Tool 3 — Profile Match Scorer
def match_profile_to_company(company_name: str) -> str:
    """
    Score how well Brijesh's profile matches a company.
    In production this would take user profile as input.
    """
    brijesh_skills = [
        "Java", "Spring Boot", "Apache Kafka",
        "PostgreSQL", "MySQL", "MongoDB",
        "AWS", "Docker", "Kubernetes",
        "Microservices", "REST APIs", "CI/CD"
    ]

    # Get company tech stack
    stack_json = analyze_company_tech(company_name)
    stack_data = json.loads(stack_json)

    if stack_data.get("found"):
        tech_stack = stack_data["tech_stack"]
        all_company_tech = (
            tech_stack.get("backend", []) +
            tech_stack.get("infra", [])
        )

        # Calculate match
        matches = [
            skill for skill in brijesh_skills
            if any(skill.lower() in tech.lower()
                   for tech in all_company_tech)
        ]

        match_score = round(len(matches) / len(all_company_tech) * 100)
        match_score = min(match_score, 95)  # cap at 95%

        return json.dumps({
            "match_score": match_score,
            "matching_skills": matches,
            "recommendation": "Strong match — apply!" if match_score > 60
                             else "Partial match — worth applying"
        })

    return json.dumps({
        "match_score": 70,
        "recommendation": "Based on general Java/microservices profile — good fit"
    })

# Tool 4 — Interview Tips Generator
def get_interview_tips(company_name: str) -> str:
    """Get specific interview tips for a company"""

    tips = {
        "mercari": [
            "Focus on system design — they love distributed systems questions",
            "Be ready to discuss Go and Java — they use both",
            "Emphasize English communication skills",
            "Show examples of taking ownership and driving projects",
            "Research their microservices architecture"
        ],
        "rakuten": [
            "Prepare for multiple interview rounds — they are thorough",
            "Show deep Java knowledge — Spring Boot internals",
            "Be ready to discuss large scale system design",
            "Demonstrate ability to work in diverse international teams",
            "Study their e-commerce platform architecture"
        ],
        "atlassian": [
            "Emphasize remote work skills and async communication",
            "Study their STAR method for behavioral questions",
            "Show experience with their products (Jira, Confluence)",
            "Discuss distributed systems and cloud architecture",
            "Be ready for take-home coding challenges"
        ],
        "razorpay": [
            "Focus on payment systems and high-scale architecture",
            "Be ready for LeetCode medium-hard problems",
            "Show startup mentality — fast delivery, ownership",
            "Discuss experience with financial systems",
            "Demonstrate knowledge of API design and security"
        ]
    }

    key = company_name.lower().replace(" ", "")
    for known_key, company_tips in tips.items():
        if known_key in key:
            return json.dumps({
                "company": company_name,
                "tips": company_tips
            }, indent=2)

    return json.dumps({
        "company": company_name,
        "tips": [
            "Research their engineering blog before interview",
            "Prepare system design examples from your experience",
            "Show specific examples with measurable impact",
            "Ask thoughtful questions about their tech challenges",
            "Demonstrate ownership mindset and proactive communication"
        ]
    })

# ── CREATE TOOLS LIST ──────────────────────────────────────────
# Java equivalent: List<Tool> tools = Arrays.asList(...)
tools = [
    Tool(
        name="Wikipedia",
        func=wikipedia_tool.run,
        description="Search Wikipedia for general information about a company. Use for company overview, history, and general facts."
    ),
    Tool(
        name="TechStackAnalyzer",
        func=analyze_company_tech,
        description="Analyze the tech stack and engineering culture of a company. Input should be the company name."
    ),
    Tool(
        name="ProfileMatcher",
        func=match_profile_to_company,
        description="Calculate how well the candidate's Java/Spring Boot profile matches a company. Input should be the company name."
    ),
    Tool(
        name="InterviewTips",
        func=get_interview_tips,
        description="Get specific interview preparation tips for a company. Input should be the company name."
    )
]

# ── AGENT PROMPT ───────────────────────────────────────────────
# ReAct prompt — Reason + Act pattern
# This tells the agent HOW to think and act
AGENT_PROMPT = PromptTemplate.from_template("""You are HireIQ's Company Research Agent.
Your job is to research companies and help candidates decide if they should apply.

You have access to these tools:
{tools}

Use this format EXACTLY:
Question: the input question you must answer
Thought: think about what you need to do
Action: the tool to use (must be one of [{tool_names}])
Action Input: the input to the tool
Observation: the result of the tool
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now have enough information to give a complete answer
Final Answer: [Complete company research report]

The Final Answer must include:
1. Company Overview
2. Tech Stack & Engineering Culture  
3. Profile Match Score & Matching Skills
4. Should you apply? (Yes/Maybe/No) with reasons
5. Interview Preparation Tips

Begin!

Question: {input}
Thought: {agent_scratchpad}""")

# ── CREATE AGENT ───────────────────────────────────────────────
# ReAct agent — Reasons then Acts
# Java equivalent: new ReActAgent(llm, tools, prompt)
agent = create_react_agent(llm, tools, AGENT_PROMPT)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,       # Show agent's thinking process!
    max_iterations=6,   # Prevent infinite loops
    handle_parsing_errors=True
)

# ── RESEARCH COMPANY ──────────────────────────────────────────
def research_company(company_name: str) -> dict:
    """
    Use AI agent to research a company autonomously.
    
    The agent will:
    1. Decide which tools to use
    2. Call tools in the right order
    3. Synthesize all information
    4. Return comprehensive report
    """
    print(f"\n🕵️ Agent researching: {company_name}")
    print("Watch the agent think step by step below:\n")
    print("="*55)

    result = agent_executor.invoke({
        "input": f"Research {company_name} for a Java/Spring Boot backend engineer with 3 years experience looking for remote work. Should they apply?"
    })

    return {
        "company":  company_name,
        "report":   result["output"],
        "status":   "success"
    }


# ── TEST ──────────────────────────────────────────────────────
if __name__ == "__main__":

    companies = ["Mercari Japan", "Atlassian"]

    for company in companies:
        print(f"\n{'='*55}")
        result = research_company(company)
        print(f"\n{'='*55}")
        print(f"📊 FINAL REPORT: {company}")
        print(f"{'='*55}")
        print(result["report"])
        print()
        input("Press Enter to research next company...")