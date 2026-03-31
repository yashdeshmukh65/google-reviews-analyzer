from database import SessionLocal
from models import Review, SearchCache
from llm_service import generate_sql_and_graph

db = SessionLocal()

print("--- Cache ---")
for c in db.query(SearchCache).all():
    print(c.business_url, c.status)

print("\n--- Reviews ---")
reviews = db.query(Review).all()
print(f"Total reviews: {len(reviews)}")
if reviews:
    print("Sample:", reviews[0].review_text, "| Sentiment:", reviews[0].sentiment)

print("\n--- LLM Test ---")
prompt = "what are the average rating"
print("Testing:", prompt)
res = generate_sql_and_graph(prompt)
print("LLM Result:", res)
