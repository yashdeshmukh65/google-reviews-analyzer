from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import io
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.csv_analyzer import CSVReviewAnalyzer

app = FastAPI(title="Google Reviews Analyser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = CSVReviewAnalyzer()

class QuestionRequest(BaseModel):
    question: str

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Load data into analyzer
        analyzer.df = df
        analyzer.business_name = df['title'].iloc[0] if not df.empty else "Unknown Business"
        
        return {
            "success": True,
            "data": {
                "business_name": analyzer.business_name,
                "total_reviews": len(df),
                "avg_rating": round(df['stars'].mean(), 2),
                "url_count": df['url'].nunique()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask-question")
async def ask_question(request: QuestionRequest):
    try:
        if analyzer.df is None:
            raise HTTPException(status_code=400, detail="No CSV data loaded")
        
        response = analyzer.ask_question(request.question)
        return {"success": True, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insights")
async def get_insights():
    try:
        if analyzer.df is None:
            raise HTTPException(status_code=400, detail="No CSV data loaded")
        
        insights = analyzer.get_insights()
        return {"success": True, "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predictions")
async def get_predictions():
    try:
        if analyzer.df is None:
            raise HTTPException(status_code=400, detail="No CSV data loaded")
        
        predictions = analyzer.get_predictive_insights()
        return {"success": True, "predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts/rating-distribution")
async def get_rating_distribution():
    try:
        if analyzer.df is None:
            raise HTTPException(status_code=400, detail="No CSV data loaded")
        
        rating_counts = analyzer.df['stars'].value_counts().sort_index()
        return {
            "success": True,
            "data": {
                "labels": rating_counts.index.tolist(),
                "values": rating_counts.values.tolist()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/charts/sentiment-pie")
async def get_sentiment_pie():
    try:
        if analyzer.df is None:
            raise HTTPException(status_code=400, detail="No CSV data loaded")
        
        sentiment_map = {5: 'Excellent', 4: 'Good', 3: 'Average', 2: 'Poor', 1: 'Terrible'}
        sentiments = analyzer.df['stars'].map(sentiment_map).value_counts()
        
        return {
            "success": True,
            "data": {
                "labels": sentiments.index.tolist(),
                "values": sentiments.values.tolist()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clear-data")
async def clear_data():
    try:
        analyzer.df = None
        analyzer.business_name = ""
        return {"success": True, "message": "Data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Google Reviews Analyser API is running!"}