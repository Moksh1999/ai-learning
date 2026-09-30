import os
from dotenv import load_dotenv
import psycopg2
import voyageai

load_dotenv()

vo = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

# Create a table with a vector column
# voyage-3.5 produces 1024-dimensional embeddings
cur.execute("""
    CREATE TABLE IF NOT EXISTS chunks (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding VECTOR(1024)
    );
""")
conn.commit()

# Your documents to store
documents = [
    "The dog ran across the park.",
    "A puppy played in the garden.",
    "I need to fix this spreadsheet formula.",
    "The cat slept on the sofa.",
    "A dog sprinted through the park.",
]

result = vo.embed(documents, model="voyage-3.5", input_type="document")
embeddings = result.embeddings

for text, emb in zip(documents, embeddings):
    cur.execute(
        "INSERT INTO chunks (content, embedding) VALUES (%s, %s)",
        (text, emb)
    )
conn.commit()

print(f"Inserted {len(documents)} chunks into Neon.")

cur.close()
conn.close()