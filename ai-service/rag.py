from groq import Groq
from sentence_transformers import SentenceTransformer
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# ── SETUP ─────────────────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model  = SentenceTransformer('all-MiniLM-L6-v2')

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


def get_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", DB_NAME),
        user=os.getenv("DB_USER", DB_USER),
        password=os.getenv("DB_PASSWORD", DB_PASSWORD),
        host=os.getenv("DB_HOST", DB_HOST),
        port=os.getenv("DB_PORT", DB_PORT)
    )

# ── STEP 1: CHUNKING ──────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """
    Split large text into smaller overlapping chunks.

    Why overlap? So context isn't lost at chunk boundaries.

    Java equivalent:
    List<String> chunks = textSplitter.split(text, chunkSize, overlap);

    Example:
    Text:    "Java is great. Spring Boot is powerful. Kafka is fast."
    Chunk 1: "Java is great. Spring Boot is powerful."
    Chunk 2: "Spring Boot is powerful. Kafka is fast."  ← overlaps!
    """
    words  = text.split()
    chunks = []
    start  = 0

    while start < len(words):
        # Take chunk_size words
        end   = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        # Move forward but keep overlap words
        start = end - overlap

    return chunks


# ── STEP 2: STORE DOCUMENTS ───────────────────────────────────
def store_document(title: str, content: str, source: str):
    """
    Chunk a document and store each chunk with its embedding.

    Java equivalent:
    documentService.ingest(title, content, source);
    """
    print(f"\n📄 Processing: {title}")

    # Split into chunks
    chunks = chunk_text(content)
    print(f"   Split into {len(chunks)} chunks")

    conn = get_db()
    cur  = conn.cursor()

    for i, chunk in enumerate(chunks):
        # Convert chunk to embedding
        embedding = model.encode(chunk).tolist()

        # Store in pgvector
        cur.execute("""
            INSERT INTO documents
            (title, content, chunk_index, source, embedding)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, chunk, i, source, embedding))

    conn.commit()
    cur.close()
    conn.close()
    print(f"   ✅ Stored {len(chunks)} chunks")


# ── STEP 3: RETRIEVE RELEVANT CHUNKS ─────────────────────────
def retrieve_relevant_chunks(query: str, limit: int = 3) -> list:
    """
    Find most relevant document chunks for a query.

    Java equivalent:
    List<DocumentChunk> chunks = vectorDB.findSimilar(query, limit);
    """
    query_embedding = model.encode(query).tolist()

    conn = get_db()
    cur  = conn.cursor()

    cur.execute("""
        SELECT
            title,
            content,
            source,
            1 - (embedding <=> %s::vector) as similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, limit))

    chunks = []
    for row in cur.fetchall():
        chunks.append({
            "title":      row[0],
            "content":    row[1],
            "source":     row[2],
            "similarity": round(float(row[3]) * 100, 1)
        })

    cur.close()
    conn.close()
    return chunks


# ── STEP 4: GENERATE ANSWER WITH CONTEXT ─────────────────────
def answer_with_rag(question: str) -> dict:
    """
    Full RAG pipeline:
    1. Find relevant chunks
    2. Build context from chunks
    3. Ask LLM with context
    4. Return answer + sources

    Java equivalent:
    RagResponse response = ragService.answer(question);
    """

    # Step 1: Retrieve relevant chunks
    chunks = retrieve_relevant_chunks(question, limit=3)

    if not chunks:
        return {
            "answer":  "I don't have enough information to answer that.",
            "sources": [],
            "chunks_used": 0
        }

    # Step 2: Build context string from chunks
    # This is what we'll give to the LLM as "real knowledge"
    context = ""
    for i, chunk in enumerate(chunks):
        context += f"\n[Source {i+1}: {chunk['title']}]\n"
        context += chunk['content']
        context += "\n"

    # Step 3: Build RAG prompt
    rag_prompt = f"""You are HireIQ, an expert career assistant.

Answer the user's question using ONLY the provided context below.
If the context doesn't contain enough information, say so honestly.
Always mention which source you used.

CONTEXT:
{context}

RULES:
1. Only use information from the context above
2. Always cite your source (e.g., "According to [Source 1]...")
3. Be specific and helpful
4. If context is insufficient, say "I don't have enough data on this"
"""

    # Step 4: Call LLM with context
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": rag_prompt},
            {"role": "user",   "content": question}
        ],
        max_tokens=1024,
        temperature=0.3  # Low — we want factual answers!
    )

    answer = response.choices[0].message.content

    # Step 5: Return answer + sources
    return {
        "answer": answer,
        "sources": [
            {
                "title":      c["title"],
                "source":     c["source"],
                "similarity": c["similarity"]
            }
            for c in chunks
        ],
        "chunks_used": len(chunks)
    }


# ── SEED CAREER KNOWLEDGE BASE ────────────────────────────────
def seed_knowledge_base():
    """
    Add career knowledge documents to the RAG system.
    In production these would be real PDFs, articles, reports.
    """

    documents = [
        {
            "title": "Java Engineer Salaries 2026",
            "source": "Tech Salary Report 2026",
            "content": """
            Java backend engineers are among the highest paid in 2026.
            In India, Java engineers with 3-5 years experience earn 
            between 15-25 LPA at product companies.
            In the US, remote Java engineers earn $70,000-$120,000 
            per year depending on company size.
            In Japan, Java engineers earn ¥7M-¥12M per year.
            Spring Boot specialists command a 20% premium over 
            general Java developers.
            Engineers with Kafka and microservices experience earn 
            30% more than average Java developers.
            AI/LLM integration skills add another 25-40% salary premium.
            """
        },
        {
            "title": "How to Get a Remote Job in Japan",
            "source": "Remote Japan Job Guide 2026",
            "content": """
            Japan is one of the best markets for remote Java engineers in 2026.
            Key platforms to find remote Japan jobs:
            - Japan Dev (japan-dev.com) — best for English speaking engineers
            - TokyoDev (tokyodev.com) — specifically for international developers
            - Wellfound Japan — startup focused roles
            
            Top companies hiring remote Java engineers in Japan:
            - Mercari — English first culture, Java microservices
            - Rakuten — large engineering team, Java heavy
            - LINE (LY Corp) — Kafka, Spring Boot, distributed systems
            - PayPay — fintech, Java backend engineers
            
            Japan timezone (JST) is UTC+9. From India (IST UTC+5:30)
            there is 3.5 hours overlap which is very manageable.
            
            Japanese companies value long term commitment, quality,
            reliability and team harmony above all else.
            Most English friendly companies do not require Japanese language.
            """
        },
        {
            "title": "How to Get a Remote Job in US Startups",
            "source": "US Remote Job Guide 2026",
            "content": """
            US startups are actively hiring remote engineers from India in 2026.
            Best platforms to find US remote jobs:
            - Wellfound (AngelList) — best for startups
            - Arc.dev — vetted remote developers
            - Turing.com — matches with US companies
            - startup.jobs — startup focused
            
            US East Coast overlap from India (IST) is 4-6 hours.
            This is sufficient for daily standups and collaboration.
            
            US startups value ownership, autonomy and shipping fast.
            They look for engineers who take initiative and communicate proactively.
            
            Salary expectations for Indian engineers working remotely for US:
            - Mid level (3-5 years): $50,000-$80,000 per year
            - Senior (5+ years): $80,000-$120,000 per year
            These are paid in USD which is 80-85x Indian rupee.
            """
        },
        {
            "title": "LLM Engineering Career Guide 2026",
            "source": "AI Career Guide 2026",
            "content": """
            LLM Engineering is the fastest growing role in tech in 2026.
            Average salary for LLM engineers globally is $130,000-$180,000.
            
            Key skills needed to become an LLM engineer:
            - Python programming (essential)
            - LangChain or LlamaIndex framework
            - RAG (Retrieval Augmented Generation)
            - Vector databases: pgvector, Pinecone, Chroma
            - Prompt engineering
            - LLM APIs: OpenAI, Anthropic Claude, Groq
            
            Java developers have a unique advantage: Spring AI and 
            LangChain4j allow LLM integration in Java. Very few 
            engineers know both Java and LLM engineering making this
            combination extremely valuable to employers.
            
            Timeline to become job ready LLM engineer: 4-6 months
            of dedicated learning and building projects.
            """
        },
        {
            "title": "Resume Tips for Backend Engineers",
            "source": "Career Advice Guide 2026",
            "content": """
            Top resume tips for backend engineers targeting remote jobs:
            
            1. Lead with impact numbers not responsibilities.
               Bad:  "Worked on microservices"
               Good: "Reduced manual effort by 70% building OSRM pipeline"
            
            2. Mention specific technologies in context not just as list.
               Bad:  "Skills: Java, Kafka, AWS"
               Good: "Built Kafka-based event pipeline processing 1M messages/day"
            
            3. Show cross-industry experience as strength.
               Working across Fintech, MarTech, SaaS shows adaptability.
            
            4. Add AI/LLM projects even if personal.
               Recruiters heavily filter for AI experience in 2026.
            
            5. For remote jobs always mention timezone overlap.
               US: mention 4-6 hour EST overlap from IST
               Japan: mention 3.5 hour JST overlap from IST
            
            6. Keep resume to 1-2 pages maximum.
               One page for under 5 years experience.
               Two pages maximum for senior roles.
            
            7. Use action verbs: Built, Designed, Led, Reduced, 
               Increased, Automated, Integrated, Architected.
            """
        }
    ]

    print("🌱 Loading knowledge base into RAG...")
    for doc in documents:
        store_document(doc["title"], doc["content"], doc["source"])

    print(f"\n✅ Knowledge base ready with {len(documents)} documents!")


# ── TEST ──────────────────────────────────────────────────────
if __name__ == "__main__":

    # Seed knowledge base first
    seed_knowledge_base()

    print("\n" + "="*55)
    print("🤖 RAG QUESTION ANSWERING TEST")
    print("="*55)

    questions = [
        "What salary can I expect as a Java engineer in Japan?",
        "How do I find remote jobs in US startups from India?",
        "What skills do I need to become an LLM engineer?",
        "How should I write my resume for remote jobs?",
    ]

    for question in questions:
        print(f"\n❓ {question}")
        result = answer_with_rag(question)
        print(f"\n💬 {result['answer'][:300]}...")
        print(f"\n📚 Sources used:")
        for source in result['sources']:
            print(f"   • {source['title']} ({source['similarity']}% match)")
        print("\n" + "-"*55)