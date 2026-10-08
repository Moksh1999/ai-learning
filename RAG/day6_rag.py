import os
from dotenv import load_dotenv
import psycopg2
import voyageai
import requests

load_dotenv()

vo = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")

def retrieve(query, top_k=3):
    result = vo.embed([query], model="voyage-3.5", input_type="query")
    query_embedding = result.embeddings[0]
    cur.execute("""
        SELECT content, embedding <=> %s::vector AS distance
        FROM resume_chunks
        ORDER BY distance
        LIMIT %s;
    """, (query_embedding, top_k))
    return cur.fetchall()

def generate_answer(query, retrieved_chunks):
    context_text = "\n\n".join([f"[{i+1}] {content}" for i, (content, distance) in enumerate(retrieved_chunks)])
    system_prompt = (
        "You are a helpful assistant. Answer the user's question using ONLY the "
        "context provided below. If the context doesn't contain enough information "
        "to answer, say so explicitly - do not make anything up.\n\n"
        f"Context:\n{context_text}"
    )
    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 300,
            "system": system_prompt,
            "messages": [{"role": "user", "content": query}]
        }
    )
    return response.json()["content"][0]["text"]

# test_queries = [
#     "How many engineers has this person led?",                     # answerable by chunks 1 & 2 - both should retrieve close
#     "What was the reduction in server requests?",                  # specific to chunk 1 only
#     "What GenAI-related feature was built?",                       # specific to chunk 3 only
#     "What programming languages does this person use in personal side projects?",  # should NOT be answerable
# ]

test_queries = [
    "What did the Data Flow Manager project involve?",          # should surface the NiFi/Keycloak chunk specifically, not the general summary
    "What recognition or award has this person received?",       # should surface the Employee of the Quarter chunk specifically
    "Does this person play any sports?",                         # the real trap - cricket chunk may retrieve due to topic overlap, but has nothing to do with the person
    "How many engineers has this person led?",                   # repeat - should still work correctly even with 5 more competing chunks now
]

for query in test_queries:
    print("=" * 70)
    print(f"Query: {query}\n")
    retrieved = retrieve(query)
    for content, distance in retrieved:
        print(f"  distance={distance:.4f}  |  {content[:70]}...")
    answer = generate_answer(query, retrieved)
    print(f"\nAnswer:\n{answer}\n")

cur.close()
conn.close()