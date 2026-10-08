import os
from dotenv import load_dotenv
import psycopg2
import voyageai

load_dotenv()

vo = voyageai.Client(api_key=os.environ.get("VOYAGE_API_KEY"))
conn = psycopg2.connect(os.environ.get("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS resume_chunks (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding VECTOR(1024)
    );
""")
conn.commit()

documents = [
    "Technical Lead and Full-Stack Engineer with 5+ years of experience building and scaling enterprise web applications using ReactJS, Node.js, and cloud-native architectures. Proven track record leading cross-functional teams of up to 18 engineers to deliver microservices-based platforms on Docker/Kubernetes with measurable impact - including a 66% reduction in server requests and 20% faster response times. Confluent CCDAK-certified, with hands-on experience in event-driven, Kafka-based architectures. Skilled in end-to-end ownership: from solution architecture and API design to CI/CD delivery and GenAI/LLM integration.",

    "Own technical architecture and delivery for enterprise web applications built on ReactJS, Node.js, and MongoDB/MySQL, supporting high-volume client deployments. Optimized database queries and backend services, reducing response times by 20%. Led cross-functional teams of up to 18 engineers, consistently shipping releases on schedule across multiple milestones while driving solution design, sprint planning, and code reviews.",

    "Implemented performance optimization techniques for frontend and backend applications. Developed core features such as AI-generated insights and the participant response cycle. Coordinated closely with the team, project manager, and solution architect to ensure smooth project delivery. Participated in system design discussions, solution architecture, and technical decision-making for scalable enterprise applications.",
]

result = vo.embed(documents, model="voyage-3.5", input_type="document")
embeddings = result.embeddings

for text, emb in zip(documents, embeddings):
    cur.execute(
        "INSERT INTO resume_chunks (content, embedding) VALUES (%s, %s)",
        (text, emb)
    )
conn.commit()

print(f"Inserted {len(documents)} chunks into resume_chunks.")
cur.close()
conn.close()