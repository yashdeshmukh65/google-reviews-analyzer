from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from database import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    business_url = Column(String, index=True)
    user_name = Column(String)
    rating = Column(Float)
    date = Column(String)
    review_text = Column(Text)
    sentiment = Column(String, default="Neutral")

class AspectSentiment(Base):
    __tablename__ = "aspect_sentiments"
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), index=True)
    aspect = Column(String, index=True)
    sentiment_score = Column(String) # 'Positive', 'Negative', 'Neutral'

class ReviewCluster(Base):
    __tablename__ = "review_clusters"
    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("reviews.id", ondelete="CASCADE"), index=True)
    cluster_id = Column(Integer, index=True)
    cluster_label = Column(String)
    business_url = Column(String, index=True) # To associate reviews with a specific business

class SearchCache(Base):
    __tablename__ = "search_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    business_url = Column(String, unique=True, index=True)
    status = Column(String) # 'pending', 'completed', 'failed'
    pos_wordcloud = Column(Text, nullable=True)
    neg_wordcloud = Column(Text, nullable=True)
