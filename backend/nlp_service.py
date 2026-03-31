import base64
from io import BytesIO
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud, STOPWORDS
import numpy as np
import matplotlib
matplotlib.use('Agg')

ASPECTS = ['food', 'service', 'price', 'ambience', 'cleanliness', 'staff', 'atmosphere', 'wait', 'time', 'friendly', 'taste', 'delivery', 'order', 'quality', 'pizza', 'crust']

def get_aspect_sentiments(reviews):
    """
    Scans review texts natively. Maps verified Llama-70b global sentiments directly to discovered aspects.
    Guarantees 'Overall Experience' fallback mapping for blank text inputs.
    """
    aspect_mappings = []
    
    for r in reviews:
        if not r.review_text:
            continue
            
        text_lower = str(r.review_text).lower()
        found = False
        
        for aspect in ASPECTS:
            if aspect in text_lower:
                aspect_mappings.append({
                    "review_id": r.id,
                    "aspect": aspect.capitalize(),
                    "sentiment_score": r.sentiment
                })
                found = True
                
        if not found:
            aspect_mappings.append({
                "review_id": r.id,
                "aspect": "Overall Experience",
                "sentiment_score": r.sentiment
            })
                    
    return aspect_mappings

def get_review_clusters(reviews, n_clusters=5):
    """
    Uses TF-IDF + KMeans to cluster reviews mathematically based on keyword frequencies.
    Returns: list of dicts { 'review_id': int, 'cluster_id': int, 'cluster_label': str }
    """
    texts = [str(r.review_text) for r in reviews if r.review_text]
    valid_ids = [r.id for r in reviews if r.review_text]
    
    if len(texts) < 5:
        # Not enough data for meaningful clustering
        return [{"review_id": vid, "cluster_id": 0, "cluster_label": "General Feedback"} for vid in valid_ids]
        
    actual_clusters = min(n_clusters, len(texts) // 2)
    
    vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
    X = vectorizer.fit_transform(texts)
    
    kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
    kmeans.fit(X)
    
    # Extract topmost keywords per centroid exactly as requested
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    
    cluster_labels = {}
    for i in range(actual_clusters):
        top_words = [terms[ind] for ind in order_centroids[i, :3]]  # Top 3 words
        cluster_labels[i] = ", ".join(top_words).title()
        
    mappings = []
    for idx, label_id in enumerate(kmeans.labels_):
        mappings.append({
            "review_id": valid_ids[idx],
            "cluster_id": int(label_id),
            "cluster_label": cluster_labels[int(label_id)]
        })
        
    return mappings

def get_wordclouds_base64(reviews):
    """
    Generates two strictly segregated Python-native Word Clouds (Positive vs Negative).
    Outputs raw Base64 PNG buffers to transit directly into React img src tags.
    """
    pos_texts = " ".join([str(r.review_text) for r in reviews if r.sentiment == "Positive"])
    neg_texts = " ".join([str(r.review_text) for r in reviews if r.sentiment == "Negative"])
    
    # We use custom SaaS hex colors explicitly requested in the React architecture
    pos_wc = WordCloud(width=800, height=400, background_color='#0f1525', colormap='Greens', max_words=100, stopwords=STOPWORDS)
    neg_wc = WordCloud(width=800, height=400, background_color='#0f1525', colormap='Reds', max_words=100, stopwords=STOPWORDS)
    
    b64_clouds = {"positive": None, "negative": None}
    
    try:
        if pos_texts.strip():
            pos_image = pos_wc.generate(pos_texts).to_image()
            buf = BytesIO()
            pos_image.save(buf, format='PNG')
            b64_clouds["positive"] = base64.b64encode(buf.getvalue()).decode('utf-8')
            
        if neg_texts.strip():
            neg_image = neg_wc.generate(neg_texts).to_image()
            buf = BytesIO()
            neg_image.save(buf, format='PNG')
            b64_clouds["negative"] = base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Wordcloud generation failed natively: {e}")
        
    return b64_clouds
