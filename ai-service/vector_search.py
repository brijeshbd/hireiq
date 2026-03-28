import psycopg2
import json
import os
from sentence_transformers import SentenceTransformer

# ── SETUP ─────────────────────────────────────────────────────

# Load embedding model — runs locally, completely FREE!
# This converts text → numbers (embeddings)
# Java equivalent: new EmbeddingModel()
print("Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')  # Small, fast, free
print("Model loaded! ✅")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Connect to PostgreSQL
# Java equivalent: DriverManager.getConnection(url, user, password)
def get_db():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", DB_NAME),
        user=os.getenv("DB_USER", DB_USER),
        password=os.getenv("DB_PASSWORD", DB_PASSWORD),
        host=os.getenv("DB_HOST", DB_HOST),
        port=os.getenv("DB_PORT", DB_PORT)
    )

# ── EMBEDDINGS ────────────────────────────────────────────────

def get_embedding(text: str) -> list:
    """
    Convert text to embedding vector.
    
    Java equivalent:
    float[] embedding = embeddingModel.encode(text);
    """
    embedding = model.encode(text)
    return embedding.tolist()  # Convert numpy array to Python list

# ── STORE JOBS ────────────────────────────────────────────────

def store_job(title, company, description, location, remote, salary_range):
    """
    Store a job with its embedding in pgvector.
    
    Java equivalent:
    jobRepository.save(new Job(title, company, embedding));
    """
    # Create text to embed — combine title + description
    text_to_embed = f"{title} {description}"
    embedding = get_embedding(text_to_embed)

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO jobs 
        (title, company, description, location, remote, salary_range, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        title, company, description,
        location, remote, salary_range,
        embedding  # pgvector handles the list automatically!
    ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Stored: {title} at {company}")

# ── SEARCH JOBS ───────────────────────────────────────────────

def search_jobs(query: str, limit: int = 5) -> list:
    """
    Find jobs similar to the query using semantic search.
    """
    # Convert query to embedding
    query_embedding = get_embedding(query)

    conn = get_db()
    cur = conn.cursor()

    # pgvector similarity search
    # <=> means cosine distance — lower = more similar
    # Java equivalent: ORDER BY cosineSimilarity(embedding, queryEmbedding)
    cur.execute("""
        SELECT 
            id,
            title,
            company,
            description,
            location,
            remote,
            salary_range,
            1 - (embedding <=> %s::vector) as similarity
        FROM jobs
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, limit))

    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "description": row[3],
            "location": row[4],
            "remote": row[5],
            "salary_range": row[6],
            "similarity": round(float(row[7]) * 100, 1)  # as percentage
        })

    cur.close()
    conn.close()
    return results

# ── SEED SAMPLE JOBS ──────────────────────────────────────────

def seed_sample_jobs():
    """Add sample jobs to the database for testing"""

    sample_jobs = [
        {
            "title": "Senior Java Backend Engineer",
            "company": "Razorpay",
            "description": "Build payment microservices using Java Spring Boot Kafka PostgreSQL AWS. Own production systems end to end.",
            "location": "Remote",
            "remote": True,
            "salary_range": "$70,000 - $100,000"
        },
        {
            "title": "Backend Software Engineer",
            "company": "Mercari Japan",
            "description": "Develop scalable backend systems using Java microservices Docker Kubernetes. Work in English friendly environment.",
            "location": "Tokyo / Remote",
            "remote": True,
            "salary_range": "¥8M - ¥12M"
        },
        {
            "title": "AI Backend Engineer",
            "company": "Fintech Startup US",
            "description": "Integrate LLM APIs into Java Spring Boot backend. Build RAG pipelines Python FastAPI pgvector.",
            "location": "Remote USA",
            "remote": True,
            "salary_range": "$90,000 - $130,000"
        },
        {
            "title": "Platform Engineer",
            "company": "Atlassian",
            "description": "Build developer tools infrastructure AWS Docker Kubernetes CI/CD pipelines Java distributed systems.",
            "location": "Remote Global",
            "remote": True,
            "salary_range": "$100,000 - $140,000"
        },
        {
            "title": "Data Engineer",
            "company": "Analytics Company",
            "description": "Build data pipelines Python SQL ETL processes machine learning model deployment.",
            "location": "Remote",
            "remote": True,
            "salary_range": "$80,000 - $110,000"
        },
        {
            "title": "Frontend React Developer",
            "company": "SaaS Startup",
            "description": "Build React TypeScript frontend applications UI components user experience design.",
            "location": "Remote",
            "remote": True,
            "salary_range": "$60,000 - $90,000"
        },
        {
            "title": "DevOps Engineer",
            "company": "Cloud Company",
            "description": "Manage AWS infrastructure Terraform Kubernetes Docker CI/CD pipelines monitoring.",
            "location": "Remote",
            "remote": True,
            "salary_range": "$85,000 - $115,000"
        },
        {
            "title": "Java Microservices Developer",
            "company": "Japan Fintech",
            "description": "Design microservices architecture Spring Boot Apache Kafka event driven systems PostgreSQL.",
            "location": "Remote Japan",
            "remote": True,
            "salary_range": "¥7M - ¥10M"
        },
        {
            "title": "LLM Engineer",
            "company": "AI Startup",
            "description": "Build LLM powered applications prompt engineering RAG vector databases LangChain Python.",
            "location": "Remote Global",
            "remote": True,
            "salary_range": "$110,000 - $150,000"
        },
        {
            "title": "Full Stack Engineer",
            "company": "Product Company",
            "description": "Build features across Java Spring Boot backend and React frontend PostgreSQL Redis.",
            "location": "Remote",
            "remote": True,
            "salary_range": "$75,000 - $105,000"
        },
    ]

    print("\n🌱 Seeding sample jobs...")
    for job in sample_jobs:
        store_job(
            job["title"],
            job["company"],
            job["description"],
            job["location"],
            job["remote"],
            job["salary_range"]
        )
    print(f"\n✅ {len(sample_jobs)} jobs stored in pgvector!")


# ── TEST ──────────────────────────────────────────────────────

if __name__ == "__main__":

    # First run — seed the database
    seed_sample_jobs()

    print("\n" + "="*50)
    print("🔍 SEMANTIC SEARCH TESTS")
    print("="*50)

    # Test 1 — Java backend search
    print("\n📌 Search: 'Java backend microservices'")
    results = search_jobs("Java backend microservices")
    for r in results[:3]:
        print(f"  {r['similarity']}% — {r['title']} at {r['company']}")

    # Test 2 — AI/LLM search
    print("\n📌 Search: 'AI and machine learning engineer'")
    results = search_jobs("AI and machine learning engineer")
    for r in results[:3]:
        print(f"  {r['similarity']}% — {r['title']} at {r['company']}")

    # Test 3 — Japan jobs
    print("\n📌 Search: 'remote job in Japan'")
    results = search_jobs("remote job in Japan")
    for r in results[:3]:
        print(f"  {r['similarity']}% — {r['title']} at {r['company']}")

    # Test 4 — Your profile!
    print("\n📌 Search: 'Java Spring Boot Kafka AWS 3 years experience'")
    results = search_jobs("Java Spring Boot Kafka AWS 3 years experience")
    for r in results[:3]:
        print(f"  {r['similarity']}% — {r['title']} at {r['company']}")

    print("\n✅ Vector search working!")