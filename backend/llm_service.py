import os
from dotenv import load_dotenv
import json
import re
from groq import Groq

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def clean_text(text: str) -> str:
    # Basic text cleaning: remove multiple spaces and emojis/special noises if needed
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def analyze_sentiments_batch(reviews_texts: list) -> list:
    """Classifies a list of review texts into Positive, Negative, Neutral utilizing LLM to parse multi-lingual/regional text."""
    if not reviews_texts:
        return []
        
    chunk_size = 50
    final_sentiments = []
    
    for i in range(0, len(reviews_texts), chunk_size):
        chunk = reviews_texts[i:i + chunk_size]
        try:
            prompt_content = "Classify each review string as strictly exactly one of these three words: 'Positive', 'Negative', or 'Neutral'. Understand mixed-code language syntax natively (e.g. Marathi/Hindi)."
            prompt_content += f"\nReturn a raw JSON object containing exactly one key 'sentiments' which holds the string array mapping.\nReviews: {json.dumps(chunk)}"
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a sentiment mapping API. Output pure JSON format: {\"sentiments\": [\"Positive\", \"Neutral\", ...]}"},
                    {"role": "user", "content": prompt_content}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            data = json.loads(response.choices[0].message.content.strip())
            sentiments = data.get("sentiments", [])
            
            if not isinstance(sentiments, list):
                final_sentiments.extend(["Neutral"] * len(chunk))
            else:
                final_sentiments.extend([s if s in ["Positive", "Negative", "Neutral"] else "Neutral" for s in sentiments])
        except Exception as e:
            print(f"Batch sentiment chunk analysis failed natively: {e}")
            final_sentiments.extend(["Neutral"] * len(chunk))
            
    # Guarantee identical array mapping matrix parity
    while len(final_sentiments) < len(reviews_texts):
        final_sentiments.append("Neutral")
    
    return final_sentiments[:len(reviews_texts)]

def generate_sql_and_graph(question: str, url: str = None) -> dict:
    """Converts natural language into a SQL query and decides graph representation simultaneously."""
    schema = '''
    Table: reviews (Core reviews data)
    Columns: id, search_url, business_url, user_name, rating, date, review_text, sentiment
    
    Table: aspect_sentiments (NLP Aspects mapping 1-to-many from reviews)
    Columns: id, review_id, aspect, sentiment_score
    
    Table: review_clusters (ML topic groupings mapping 1-to-1 from reviews)
    Columns: id, review_id, cluster_id, cluster_label
    '''
    
    safe_url = url.replace("'", "''") if url else ""
    url_constraint = f"IMPORTANT: You MUST rigorously append `WHERE business_url = '{safe_url}'` (or an equivalent JOIN constraint filtering `reviews.business_url = '{safe_url}'`) in your SQL queries to prevent fetching corrupted arbitrary global data matching different targets!" if safe_url else ""
    
    prompt = f"""
    You are an expert SQL assistant and data visualization expert.
    Given the Database Schema and the User Query, determine the standard SQLite SQL query, and decide if a chart (line, bar, pie) would be useful to visualize it.
    
    Database Schema:
    {schema}
    
    User Query: "{question}"
    {url_constraint}
    
    CRITICAL RULE: For graphical outputs, the `SELECT` clause MUST have the independent categorical column (Labels/X-axis) placed FIRST, and the quantitative numerical column (Values/Y-axis) placed SECOND. (e.g. `SELECT sentiment, COUNT(*) FROM ...`)
    
    Respond strictly in the following JSON format without any markdown wrappers:
    {{
        "sql": "SELECT ...",
        "needs_graph": true_or_false,
        "chart_type": "line_or_bar_or_pie_or_null",
        "x_label": "concept for x axis",
        "y_label": "concept for y axis"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You must output strictly valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        response_str = response.choices[0].message.content.strip()
        response_str = response_str.replace("```json", "").replace("```", "").strip()
        return json.loads(response_str)
    except Exception as e:
        print(f"SQL/Graph generation failed: {e}")
        return {"sql": "", "needs_graph": False, "chart_type": None}

def refine_answer(question: str, sql_result: list) -> str:
    """Converts the raw SQL result into a refined natural language answer."""
    prompt = f"""
    The user asked: "{question}"
    The database returned the following data: {sql_result}
    
    Formulate a clear, concise, and professional natural language answer based ONLY on the provided data.
    """
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Answer refinement failed: {e}")
        return str(sql_result)
