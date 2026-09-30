import os
from dotenv import load_dotenv
import voyageai

load_dotenv()
vo = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))

sentences = [
    "The dog ran across the park.",
    "A puppy played in the garden.",
    "I need to fix this spreadsheet formula.",
    "The cat slept on the sofa.",
    "A dog sprinted through the park."
]

result = vo.embed(sentences, model="voyage-3.5", input_type="document")
embeddings = result.embeddings

def cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x * x for x in a) ** 0.5
    mag_b = sum(x * x for x in b) ** 0.5
    return dot / (mag_a * mag_b)

print("Vector length (dimensions):", len(embeddings[0]))
print()

for i in range(len(sentences)):
    for j in range(i + 1, len(sentences)):
        sim = cosine_similarity(embeddings[i], embeddings[j])
        print(f"'{sentences[i]}'  <->  '{sentences[j]}'")
        print(f"   similarity: {sim:.4f}\n")