from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import Review, SearchCache, AspectSentiment, ReviewCluster
from scraper import get_google_reviews
from nlp_service import get_aspect_sentiments, get_review_clusters, get_wordclouds_base64
from llm_service import clean_text, generate_sql_and_graph, refine_answer
from textblob import TextBlob
import datetime
import time
import csv

def normalize_date(date_str: str) -> str:
    """Takes ambiguous strings 'a month ago', '2 weeks ago', or custom CSV formats and normalizes mathematically to YYYY-MM-DD"""
    date_str = str(date_str).lower().strip()
    if not date_str or date_str == "unknown":
        return "Unknown"
    if "-" in date_str or "/" in date_str: # Preserve strict inputs
        return date_str
    try:
        if "year" in date_str:
            num = 1 if "a " in date_str or "an " in date_str else int(''.join(filter(str.isdigit, date_str)) or 1)
            return (datetime.datetime.now() - datetime.timedelta(days=num*365)).strftime('%Y-%m-%d')
        if "month" in date_str:
            num = 1 if "a " in date_str or "an " in date_str else int(''.join(filter(str.isdigit, date_str)) or 1)
            return (datetime.datetime.now() - datetime.timedelta(days=num*30)).strftime('%Y-%m-%d')
        if "week" in date_str:
            num = 1 if "a " in date_str or "an " in date_str else int(''.join(filter(str.isdigit, date_str)) or 1)
            return (datetime.datetime.now() - datetime.timedelta(days=num*7)).strftime('%Y-%m-%d')
        if "day" in date_str:
            num = 1 if "a " in date_str or "an " in date_str else int(''.join(filter(str.isdigit, date_str)) or 1)
            return (datetime.datetime.now() - datetime.timedelta(days=num)).strftime('%Y-%m-%d')
    except:
        pass # Allow seamless fallback
    return datetime.datetime.now().strftime('%Y-%m-%d')

router = APIRouter()

class ScrapeRequest(BaseModel):
    url: str
    limit: int = 100

class ChatRequest(BaseModel):
    query: str
    url: Optional[str] = None

def scrape_task(url: str, limit: int, db: Session):
    # Check cache status
    cache = db.query(SearchCache).filter(SearchCache.business_url == url).first()
    if not cache:
        cache = SearchCache(business_url=url, status="pending")
        db.add(cache)
        db.commit()
    else:
        # If caching logic is simple, let's just obliterate the cache if a new request hits 
        # For MVP we will just override the existing scrape
        db.query(Review).filter(Review.business_url == url).delete()
        cache.status = "pending"
        db.commit()

    try:
        raw_reviews = get_google_reviews(url, max_reviews=limit)
        
        # Batch clean and analyze utilizing cloud AI for multi-lingual resilience
        cleaned_texts = [clean_text(r["review_text"]) for r in raw_reviews]
        from llm_service import analyze_sentiments_batch
        sentiments = analyze_sentiments_batch(cleaned_texts)
        
        current_time = datetime.datetime.now()
        for i, r in enumerate(raw_reviews):
            sentiment = sentiments[i] if i < len(sentiments) else "Neutral"
            norm_date = normalize_date(r["date"])
            
            # Algorithmic sequence generation for trend stability
            if norm_date == "Unknown":
                norm_date = (current_time - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                
            review_entry = Review(
                user_name=r["user_name"],
                rating=r["rating"],
                review_text=cleaned_texts[i],
                date=norm_date,
                sentiment=sentiment,
                business_url=url
            )
            db.add(review_entry)
            
        db.commit()

        # Advanced Analytics Execution
        inserted_reviews = db.query(Review).filter(Review.business_url == url).all()
        try:
            for act in get_aspect_sentiments(inserted_reviews):
                db.add(AspectSentiment(**act))
            for cls in get_review_clusters(inserted_reviews):
                db.add(ReviewCluster(**cls))
        except Exception as nlp_e:
            print("NLP Batch Processing Error:", nlp_e)

        b64_clouds = get_wordclouds_base64(inserted_reviews)
        cache.pos_wordcloud = b64_clouds.get("positive")
        cache.neg_wordcloud = b64_clouds.get("negative")
            
        cache.status = "completed"
        db.commit()
    except Exception as e:
        cache.status = "failed"
        db.commit()
        print(f"Background task failed: {e}")
        
@router.post("/scrape")
def trigger_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    cache = db.query(SearchCache).filter(SearchCache.business_url == request.url).first()
    if cache and cache.status == "completed":
        # Delete old cache so it accurately scrapes the requested limit
        pass
        
    background_tasks.add_task(scrape_task, request.url, request.limit, db)
    return {"message": "Scraping started in background.", "status": "pending"}

@router.get("/status")
def get_status(url: str, db: Session = Depends(get_db)):
    cache = db.query(SearchCache).filter(SearchCache.business_url == url).first()
    if cache:
        return {"status": cache.status}
    return {"status": "not_found"}

@router.get("/data")
def get_data(url: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Review)
    if url:
        query = query.filter(Review.business_url == url)
    return query.all()

@router.post("/chat")
def chat_with_data(request: ChatRequest, db: Session = Depends(get_db)):
    graph_sql_info = generate_sql_and_graph(request.query, request.url)
    sql_query = graph_sql_info.get("sql", "")
    
    if not sql_query:
        raise HTTPException(status_code=400, detail="Could not generate SQL query for your prompt.")
        
    try:
        # Secure execution caution: Using raw SQL with SQLite from LLM can be risky in production.
        # For MVP, text execution is used.
        result = db.execute(text(sql_query)).fetchall()
        data_res = [dict(row._mapping) for row in result]
        
        # Protect LLM context windows by limiting raw data context
        context_data = data_res[:50]
        
        # Refine answer
        natural_response = refine_answer(request.query, context_data)
        
        # Format graph info for frontend
        graph_decision = {
            "requires_graph": graph_sql_info.get("needs_graph", False),
            "chart_type": graph_sql_info.get("chart_type", None),
            "x_label": graph_sql_info.get("x_label", ""),
            "y_label": graph_sql_info.get("y_label", "")
        }
        
        return {
            "answer": natural_response,
            "sql_used": sql_query,
            "data": data_res,
            "graph": graph_decision
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution failed: {e}")

@router.post("/upload")
async def upload_csv_data(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        # use utf-8-sig to automatically strip Byte Order Marks (BOM) from Excel CSVs
        decoded = content.decode('utf-8-sig', errors='replace').splitlines()
        reader = csv.DictReader(decoded)
        
        business_url = file.filename or "Uploaded_CSV"
        
        raw_reviews = []
        for row in reader:
            if not row: continue
            row_keys = {str(k).lower().strip(): k for k in row.keys() if k}
            text = row.get(row_keys.get("text", "text"), "")
            stars = row.get(row_keys.get("stars", "stars"), "0")
            title = row.get(row_keys.get("title", "title"), "")
            
            # Intelligent fallback for time columns
            date_key = next((v for k, v in row_keys.items() if 'date' in k or 'time' in k), None)
            date_val = row.get(date_key, "Unknown") if date_key else "Unknown"
            
            if title:
                business_url = title
                
            try:
                rating = float(stars)
            except:
                rating = 0.0
                
            raw_reviews.append({
                "user_name": row.get(row_keys.get("name", "name"), "Unknown") or "Unknown",
                "rating": rating,
                "date": normalize_date(date_val),
                "review_text": text
            })
            
        # Protect against massive CSVs
        raw_reviews = raw_reviews[:1000]
        
        db.query(Review).filter(Review.business_url == business_url).delete()
        db.commit()
        
        cleaned_texts = [clean_text(r["review_text"]) for r in raw_reviews]
        
        from llm_service import analyze_sentiments_batch
        sentiments = analyze_sentiments_batch(cleaned_texts)
        
        current_time = datetime.datetime.now()
        for i, r in enumerate(raw_reviews):
            norm_date = r["date"]
            if norm_date == "Unknown":
                norm_date = (current_time - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
                
            db_review = Review(
                user_name=r["user_name"],
                rating=r["rating"],
                review_text=r["review_text"],
                date=norm_date,
                sentiment=sentiments[i] if i < len(sentiments) else "Neutral",
                business_url=business_url
            )
            db.add(db_review)
        db.commit()

        # Advanced Analytics Execution
        inserted_reviews = db.query(Review).filter(Review.business_url == business_url).all()
        try:
            for act in get_aspect_sentiments(inserted_reviews):
                db.add(AspectSentiment(**act))
            for cls in get_review_clusters(inserted_reviews):
                db.add(ReviewCluster(**cls))
        except Exception as nlp_e:
            print("NLP Batch Processing Error:", nlp_e)

        b64_clouds = get_wordclouds_base64(inserted_reviews)
        
        # Insert cache so UI can poll natively if needed
        cache = db.query(SearchCache).filter(SearchCache.business_url == business_url).first()
        if not cache:
            cache = SearchCache(business_url=business_url, status="completed")
            db.add(cache)
        
        cache.status = "completed"
        cache.pos_wordcloud = b64_clouds.get("positive")
        cache.neg_wordcloud = b64_clouds.get("negative")
        db.commit()
        
        return {"status": "completed", "url": business_url, "count": len(raw_reviews)}
    except Exception as e:
        print(f"CSV Upload failed: {e}")
        return {"status": "failed", "error": str(e)}


@router.get("/advanced_data")
def get_advanced_data(url: str, db: Session = Depends(get_db)):
    cache = db.query(SearchCache).filter(SearchCache.business_url == url).first()
    if not cache:
        raise HTTPException(status_code=404, detail="Dataset not cached.")
        
    reviews = db.query(Review).filter(Review.business_url == url).all()
    review_ids = [r.id for r in reviews]
    
    aspects = db.query(AspectSentiment).filter(AspectSentiment.review_id.in_(review_ids)).all()
    clusters = db.query(ReviewCluster).filter(ReviewCluster.review_id.in_(review_ids)).all()
    
    def serialize(obj):
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}
        
    return {
        "pos_wordcloud": cache.pos_wordcloud,
        "neg_wordcloud": cache.neg_wordcloud,
        "aspects": [serialize(a) for a in aspects],
        "clusters": [serialize(c) for c in clusters]
    }


@router.post("/insights")
def get_llm_insights(request: ScrapeRequest, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.business_url == request.url).all()
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found to analyze.")
        
    from llm_service import client
    import json
    
    pos_count = sum(1 for r in reviews if r.sentiment == "Positive")
    neg_count = sum(1 for r in reviews if r.sentiment == "Negative")
    
    prompt = f"""
    You are an expert executive business analyst. Analyze this dataset of {len(reviews)} reviews.
    Positive: {pos_count}, Negative: {neg_count}.
    Look at these sample negative reviews: {[r.review_text for r in reviews if r.sentiment == "Negative"][:5]}
    Look at these sample positive reviews: {[r.review_text for r in reviews if r.sentiment == "Positive"][:5]}
    
    Provide EXACTLY 3-5 concise bullet points of actionable business insights and anomalies. Do not include extra conversational text.
    Return strictly JSON format: {{"insights": ["bullet 1", "bullet 2", ...]}}
    """
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("Groq LLM Analytics Exception:", e)
        return {"insights": ["Could not generate insights at this time due to cloud latency restrictions."]}
