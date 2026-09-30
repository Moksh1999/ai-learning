import os
from dotenv import load_dotenv
import psycopg2
import voyageai

load_dotenv()

vo = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

# The new question we want to find relevant chunks for
query = "Tell me about a young dog outdoors"

# Embed the query - note input_type="query", not "document"
# Voyage optimizes the vector slightly differently depending on which side you're on
result = vo.embed([query], model="voyage-3.5", input_type="query")
query_embedding = result.embeddings[0]

# <=> is pgvector's cosine distance operator (lower = more similar)
# We ask Postgres to sort all rows by distance to our query vector, and give us the top 3
cur.execute("""
    SELECT content, embedding <=> %s::vector AS distance
    FROM chunks
    ORDER BY distance
    LIMIT 3;
""", (query_embedding,))

results = cur.fetchall()

print(f"Query: {query}\n")
print("Top matches:")
for content, distance in results:
    print(f"  distance={distance:.4f}  |  {content}")

cur.close()
conn.close()