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
        FROM chunks
        ORDER BY distance
        LIMIT %s;
    """, (query_embedding, top_k))

    return cur.fetchall()

def generate_answer(query, retrieved_chunks):
    # Build the context block from retrieved chunks
    context_text = "\n".join([f"- {content}" for content, distance in retrieved_chunks])

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
            "messages": [
                {"role": "user", "content": query}
            ]
        }
    )

    data = response.json()
    return data["content"][0]["text"]

# --- Run the full pipeline ---
# query = "Tell me about a young dog outdoors"
query = "What's the weather like today?"

print(f"Query: {query}\n")

retrieved = retrieve(query)
print("Retrieved chunks:")
for content, distance in retrieved:
    print(f"  distance={distance:.4f}  |  {content}")

answer = generate_answer(query, retrieved)
print(f"\nAnswer:\n{answer}")

cur.close()
conn.close()