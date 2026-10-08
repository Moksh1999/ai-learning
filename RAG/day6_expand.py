import os
from dotenv import load_dotenv
import psycopg2
import voyageai

load_dotenv()

vo = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

new_documents = [
    # Real, relevant - Data Flow Manager project
    "Developed scalable RESTful APIs and microservices for a Data Flow Manager project, implementing authentication and authorization mechanisms and optimizing backend performance. Designed the database structure for scheduling and managing deployments on NiFi clusters, and integrated Azure AD and Keycloak SSO for secure authentication and enterprise access.",

    # Real, relevant - multi-tenant admin portal
    "Built a multi-tenant admin portal enabling CRUD operations on users per tenant, suspending accounts, and managing subscriptions, payment types, and user types. The portal also handled contact and account management, marketing integration such as email campaigns and lead scoring, and customer support ticketing tied to each account.",

    # Real, relevant - achievement
    "Received the Employee of the Quarter award consecutively for delivering a critical project ahead of schedule.",

    # Deliberately irrelevant filler #1
    "The best way to make masala chai is to boil water with cardamom and ginger before adding tea leaves and simmering with milk.",

    # Deliberately irrelevant filler #2
    "Cricket is a widely followed sport in India, with formats like Test matches, ODIs, and T20 games each having different rules and durations.",
]

result = vo.embed(new_documents, model="voyage-3.5", input_type="document")
embeddings = result.embeddings

for text, emb in zip(new_documents, embeddings):
    cur.execute(
        "INSERT INTO resume_chunks (content, embedding) VALUES (%s, %s)",
        (text, emb)
    )
conn.commit()

cur.execute("SELECT COUNT(*) FROM resume_chunks;")
total = cur.fetchone()[0]
print(f"Inserted {len(new_documents)} new chunks. Total in table: {total}")

cur.close()
conn.close()