import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import json
import numpy as np

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False

# Load .env only if available (for local development)
try:
    load_dotenv()
except:
    pass

class CSVReviewAnalyzer:
    def __init__(self):
        # Get API key from environment (works for both local .env and Render env vars)
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.df = None
        self.business_name = ""
    
    def load_json_data(self, reviews_data, business_info):
        """Load reviews from JSON data"""
        try:
            # Convert JSON data to DataFrame with consistent column names
            df_data = []
            for review in reviews_data:
                df_data.append({
                    'reviewer_name': review.get('reviewer_name', 'Anonymous'),
                    'rating': review.get('rating', 3),
                    'review_text': review.get('review_text', ''),
                    'review_date': review.get('review_date', ''),
                    'title': business_info.get('name', 'Unknown Business'),
                    'url': business_info.get('url', ''),
                    'stars': review.get('rating', 3),  # Keep for backward compatibility
                    'text': review.get('review_text', ''),  # Keep for backward compatibility
                    'date': review.get('review_date', '')  # Keep for backward compatibility
                })
            
            self.df = pd.DataFrame(df_data)
            self.business_name = business_info.get('name', 'Unknown Business')
            
            if self.df.empty:
                return False, "No review data found"
            
            return True, {
                'business_name': self.business_name,
                'total_reviews': len(self.df),
                'avg_rating': round(self.df['rating'].mean(), 2),
                'scraped_at': business_info.get('scraped_at', 'Unknown')
            }
        except Exception as e:
            return False, f"Error loading data: {str(e)}"
    
    def get_data_summary(self):
        """Get summary statistics of the data"""
        if self.df is None:
            return "No data loaded"
        
        summary = f"""
        **Business**: {self.business_name}
        **Total Reviews**: {len(self.df)}
        **Average Rating**: {self.df['stars'].mean():.2f}/5
        **Rating Distribution**:
        - 5 stars: {len(self.df[self.df['stars'] == 5])} reviews
        - 4 stars: {len(self.df[self.df['stars'] == 4])} reviews  
        - 3 stars: {len(self.df[self.df['stars'] == 3])} reviews
        - 2 stars: {len(self.df[self.df['stars'] == 2])} reviews
        - 1 star: {len(self.df[self.df['stars'] == 1])} reviews
        """
        return summary
    
    def ask_question(self, question):
        """Answer questions about the review data using LLM"""
        if self.df is None:
            return "Please upload a CSV file first."
        
        try:
            # Prepare data context for LLM
            data_context = self._prepare_data_context()
            
            prompt = f"""
            You are analyzing reviews for {self.business_name}. Answer the question using ONLY the actual data provided.
            
            REVIEW DATA:
            {data_context}
            
            QUESTION: {question}
            
            Rules:
            - Use ONLY real reviewer names from the data (ignore "Unknown" or "Reviewer_X" entries)
            - If asking about recent reviewers, list actual names from the data
            - Be specific and factual based on the data
            - Keep answer short (2-3 sentences)
            - If data is limited, say so clearly
            """
            
            response = self.model.generate_content(prompt)
            if response and response.text:
                return response.text
            else:
                return "Sorry, I couldn't generate a response. Please try again."
                
        except Exception as e:
            return f"Error: {str(e)}. Please check your API key and try again."
    
    def _prepare_data_context(self):
        """Prepare concise data context for LLM"""
        # Clean data first
        clean_df = self.df.dropna(subset=['text', 'stars'])
        
        # Basic stats
        stats = f"""
        Business: {self.business_name}
        Total Reviews: {len(clean_df)}
        Average Rating: {clean_df['stars'].mean():.2f}/5
        
        Rating Distribution:
        {clean_df['stars'].value_counts().sort_index().to_string()}
        
        Sample Reviews:
        """
        
        # Add sample reviews from each rating category
        sample_reviews = ""
        for rating in [5, 4, 3, 2, 1]:
            rating_reviews = clean_df[clean_df['stars'] == rating]
            if not rating_reviews.empty:
                sample = rating_reviews.head(3)  # Get more samples
                for _, review in sample.iterrows():
                    text = str(review['text']).strip()
                    reviewer = str(review.get('reviewer_name', 'Anonymous'))
                    if text and text != 'nan':
                        sample_reviews += f"\n{rating}⭐ - {reviewer}: {text[:300]}..."
        
        return stats + sample_reviews
    
    def get_insights(self):
        """Get automated insights about the business"""
        if self.df is None:
            return "No data loaded"
        
        prompt = f"""
        Analyze these customer reviews for {self.business_name} and provide key insights:
        
        {self._prepare_data_context()}
        
        Please provide:
        1. Overall sentiment analysis
        2. Common positive themes
        3. Common complaints/issues
        4. Recommendations for improvement
        5. Strengths to maintain
        
        Be specific and actionable.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating insights: {str(e)}"
    
    def get_rating_distribution(self):
        """Create rating distribution chart"""
        if self.df is None:
            return None
        
        rating_counts = self.df['stars'].value_counts().sort_index()
        
        fig = px.bar(
            x=rating_counts.index,
            y=rating_counts.values,
            title=f"Rating Distribution for {self.business_name}",
            labels={'x': 'Star Rating', 'y': 'Number of Reviews'},
            color=rating_counts.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            showlegend=False,
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray'),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig
    
    def get_sentiment_pie(self):
        """Create sentiment pie chart"""
        if self.df is None:
            return None
        
        # Categorize ratings
        sentiment_map = {
            5: 'Excellent', 4: 'Good', 3: 'Average', 2: 'Poor', 1: 'Terrible'
        }
        
        sentiments = self.df['stars'].map(sentiment_map).value_counts()
        
        fig = px.pie(
            values=sentiments.values,
            names=sentiments.index,
            title=f"Sentiment Analysis for {self.business_name}",
            color_discrete_map={
                'Excellent': '#2E8B57',
                'Good': '#90EE90', 
                'Average': '#FFD700',
                'Poor': '#FFA500',
                'Terrible': '#FF6347'
            }
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig
    
    def get_word_cloud_data(self, min_rating=1, max_rating=5):
        """Generate word cloud data"""
        if self.df is None or not WORDCLOUD_AVAILABLE:
            return None
        
        # Filter by rating range
        filtered_df = self.df[
            (self.df['stars'] >= min_rating) & 
            (self.df['stars'] <= max_rating)
        ]
        
        # Combine all text
        all_text = ' '.join(filtered_df['text'].dropna().astype(str))
        
        # Clean text
        all_text = re.sub(r'[^a-zA-Z\s]', '', all_text.lower())
        
        # Generate word cloud
        try:
            wordcloud = WordCloud(
                width=800, height=400,
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(all_text)
            
            return wordcloud
        except:
            return None
    
    def get_rating_trend(self):
        """Create rating trend over time if date available"""
        if self.df is None:
            return None
        
        # Simple rating distribution by index (proxy for time)
        df_indexed = self.df.reset_index()
        
        fig = px.scatter(
            df_indexed,
            x='index',
            y='stars',
            title=f"Rating Pattern for {self.business_name}",
            labels={'index': 'Review Order', 'stars': 'Star Rating'},
            color='stars',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray'),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig
    
    def get_top_words(self, rating_filter=None, top_n=10):
        """Get most common words"""
        if self.df is None:
            return None
        
        df_filtered = self.df.copy()
        if rating_filter:
            df_filtered = df_filtered[df_filtered['stars'].isin(rating_filter)]
        
        # Combine all text
        all_text = ' '.join(df_filtered['text'].dropna().astype(str))
        
        # Clean and split words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
        
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        words = [word for word in words if word not in stop_words]
        
        # Count words
        word_counts = Counter(words).most_common(top_n)
        
        if not word_counts:
            return None
        
        words, counts = zip(*word_counts)
        
        fig = px.bar(
            x=list(counts),
            y=list(words),
            orientation='h',
            title=f"Most Common Words in Reviews",
            labels={'x': 'Frequency', 'y': 'Words'}
        )
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='lightgray'),
            yaxis=dict(showgrid=True, gridcolor='lightgray', categoryorder='total ascending'),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig
    
    def get_predictive_insights(self):
        """Generate predictive analytics using LLM"""
        if self.df is None:
            return "No data loaded"
        
        # Prepare enhanced data context for predictions
        data_context = self._prepare_predictive_context()
        
        prompt = f"""
        You are a business analytics expert with predictive modeling capabilities. Analyze this review data for {self.business_name} and provide:
        
        {data_context}
        
        PREDICTIVE ANALYSIS:
        1. **Trend Forecasting**: Based on rating patterns, predict if ratings will improve, decline, or stay stable in next 3 months
        2. **Rating Predictions**: Estimate likely average rating range for next quarter
        3. **Customer Behavior Insights**: Predict customer retention, satisfaction trends, and potential churn risks
        4. **Business Risks**: Identify early warning signs and potential issues
        5. **Growth Opportunities**: Predict areas for business expansion or improvement
        6. **Seasonal Patterns**: Identify any cyclical trends in customer feedback
        
        Provide specific predictions with confidence levels and actionable recommendations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating predictions: {str(e)}"
    
    def _prepare_predictive_context(self):
        """Prepare enhanced data context for predictive analysis"""
        clean_df = self.df.dropna(subset=['text', 'stars'])
        
        # Calculate trends
        recent_reviews = clean_df.tail(len(clean_df)//3)  # Last 1/3 of reviews
        older_reviews = clean_df.head(len(clean_df)//3)   # First 1/3 of reviews
        
        recent_avg = recent_reviews['stars'].mean() if not recent_reviews.empty else 0
        older_avg = older_reviews['stars'].mean() if not older_reviews.empty else 0
        trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        
        # Rating distribution analysis
        rating_dist = clean_df['stars'].value_counts().sort_index()
        
        # Text analysis for patterns
        positive_reviews = clean_df[clean_df['stars'] >= 4]['text'].tolist()
        negative_reviews = clean_df[clean_df['stars'] <= 2]['text'].tolist()
        
        context = f"""
        BUSINESS DATA:
        - Business: {self.business_name}
        - Total Reviews: {len(clean_df)}
        - Overall Average Rating: {clean_df['stars'].mean():.2f}/5
        - Recent Trend: {trend_direction} (Recent: {recent_avg:.2f} vs Older: {older_avg:.2f})
        
        RATING DISTRIBUTION:
        {rating_dist.to_string()}
        
        SAMPLE POSITIVE FEEDBACK:
        {' | '.join(positive_reviews[:3]) if positive_reviews else 'None'}
        
        SAMPLE NEGATIVE FEEDBACK:
        {' | '.join(negative_reviews[:3]) if negative_reviews else 'None'}
        
        REVIEW VOLUME PATTERN:
        - Early reviews: {len(older_reviews)}
        - Recent reviews: {len(recent_reviews)}
        """
        
        return context
    
    def get_customer_behavior_analysis(self):
        """Analyze customer behavior patterns"""
        if self.df is None:
            return None
        
        clean_df = self.df.dropna(subset=['text', 'stars'])
        
        # Behavior metrics
        total_reviews = len(clean_df)
        avg_rating = clean_df['stars'].mean()
        
        # Satisfaction levels
        highly_satisfied = len(clean_df[clean_df['stars'] == 5]) / total_reviews * 100
        satisfied = len(clean_df[clean_df['stars'] == 4]) / total_reviews * 100
        neutral = len(clean_df[clean_df['stars'] == 3]) / total_reviews * 100
        dissatisfied = len(clean_df[clean_df['stars'] <= 2]) / total_reviews * 100
        
        # Create behavior chart
        behavior_data = {
            'Highly Satisfied (5⭐)': highly_satisfied,
            'Satisfied (4⭐)': satisfied,
            'Neutral (3⭐)': neutral,
            'Dissatisfied (≤2⭐)': dissatisfied
        }
        
        fig = px.bar(
            x=list(behavior_data.keys()),
            y=list(behavior_data.values()),
            title=f"Customer Satisfaction Distribution - {self.business_name}",
            labels={'x': 'Satisfaction Level', 'y': 'Percentage of Customers'},
            color=list(behavior_data.values()),
            color_continuous_scale='RdYlGn'
        )
        
        return fig
    
    def get_trend_forecast_chart(self):
        """Create trend forecast visualization"""
        if self.df is None:
            return None
        
        clean_df = self.df.dropna(subset=['text', 'stars'])
        
        # Group reviews into time segments
        segment_size = max(1, len(clean_df) // 6)  # 6 time segments
        segments = []
        
        for i in range(0, len(clean_df), segment_size):
            segment = clean_df.iloc[i:i+segment_size]
            if not segment.empty:
                segments.append({
                    'Period': f"Period {len(segments)+1}",
                    'Average_Rating': segment['stars'].mean(),
                    'Review_Count': len(segment)
                })
        
        if len(segments) < 2:
            return None
        
        # Create trend chart
        periods = [s['Period'] for s in segments]
        ratings = [s['Average_Rating'] for s in segments]
        
        fig = px.line(
            x=periods,
            y=ratings,
            title=f"Rating Trend Analysis - {self.business_name}",
            labels={'x': 'Time Period', 'y': 'Average Rating'},
            markers=True
        )
        
        # Add trend line
        fig.add_hline(y=clean_df['stars'].mean(), line_dash="dash", 
                     annotation_text=f"Overall Average: {clean_df['stars'].mean():.2f}")
        
        return fig
    
    def get_word_cloud_figure(self, rating_type="all"):
        """Generate word cloud as matplotlib figure for Streamlit"""
        if self.df is None:
            return None
        
        if not WORDCLOUD_AVAILABLE:
            # Create a simple text-based visualization instead
            return self.create_text_wordcloud_fallback(rating_type)
        
        # Set rating range based on type
        if rating_type == "positive":
            min_rating, max_rating = 4, 5
            title = "Word Cloud - Positive Reviews (4-5 stars)"
        elif rating_type == "negative":
            min_rating, max_rating = 1, 2
            title = "Word Cloud - Negative Reviews (1-2 stars)"
        else:
            min_rating, max_rating = 1, 5
            title = "Word Cloud - All Reviews"
        
        wordcloud = self.get_word_cloud_data(min_rating, max_rating)
        if wordcloud is None:
            return None
        
        # Create smaller matplotlib figure with border
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(title, fontsize=14, pad=15)
        
        # Add border
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_linewidth(2)
            spine.set_edgecolor('#ddd')
        
        plt.tight_layout()
        return fig
    
    def create_text_wordcloud_fallback(self, rating_type):
        """Create text-based word frequency chart when wordcloud not available"""
        if rating_type == "positive":
            rating_filter = [4, 5]
            title = "Top Words - Positive Reviews (4-5 stars)"
        elif rating_type == "negative":
            rating_filter = [1, 2]
            title = "Top Words - Negative Reviews (1-2 stars)"
        else:
            rating_filter = [1, 2, 3, 4, 5]
            title = "Top Words - All Reviews"
        
        # Get top words
        fig = self.get_top_words(rating_filter, top_n=15)
        if fig:
            fig.update_layout(title=title, height=400)
        return fig
    
    def get_review_length_distribution(self):
        """Analyze review length distribution"""
        if self.df is None:
            return None
        
        # Calculate review lengths
        review_lengths = self.df['text'].dropna().astype(str).str.len()
        
        # Categorize lengths
        length_categories = []
        for length in review_lengths:
            if length < 50:
                length_categories.append('Short (<50 chars)')
            elif length < 150:
                length_categories.append('Medium (50-150 chars)')
            elif length < 300:
                length_categories.append('Long (150-300 chars)')
            else:
                length_categories.append('Very Long (>300 chars)')
        
        length_counts = pd.Series(length_categories).value_counts()
        
        fig = px.pie(
            values=length_counts.values,
            names=length_counts.index,
            title=f"Review Length Distribution - {self.business_name}",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        return fig
    
    def get_rating_vs_length_scatter(self):
        """Scatter plot of rating vs review length"""
        if self.df is None:
            return None
        
        clean_df = self.df.dropna(subset=['text', 'stars'])
        clean_df['review_length'] = clean_df['text'].astype(str).str.len()
        
        fig = px.scatter(
            clean_df,
            x='review_length',
            y='stars',
            title=f"Rating vs Review Length - {self.business_name}",
            labels={'review_length': 'Review Length (characters)', 'stars': 'Star Rating'},
            color='stars',
            color_continuous_scale='RdYlGn',
            opacity=0.6
        )
        
        return fig
    
    def get_sentiment_by_rating(self):
        """Detailed sentiment analysis by rating"""
        if self.df is None:
            return None
        
        # Create sentiment categories
        sentiment_data = []
        for rating in [1, 2, 3, 4, 5]:
            count = len(self.df[self.df['stars'] == rating])
            if rating >= 4:
                sentiment = 'Positive'
                color = '#2E8B57'
            elif rating == 3:
                sentiment = 'Neutral'
                color = '#FFD700'
            else:
                sentiment = 'Negative'
                color = '#FF6347'
            
            sentiment_data.append({
                'Rating': f"{rating} Star",
                'Count': count,
                'Sentiment': sentiment,
                'Color': color
            })
        
        df_sentiment = pd.DataFrame(sentiment_data)
        
        fig = px.bar(
            df_sentiment,
            x='Rating',
            y='Count',
            color='Sentiment',
            title=f"Detailed Sentiment Analysis - {self.business_name}",
            labels={'Count': 'Number of Reviews'},
            color_discrete_map={'Positive': '#2E8B57', 'Neutral': '#FFD700', 'Negative': '#FF6347'}
        )
        
        return fig
    
    def get_monthly_trend_heatmap(self):
        """Create a heatmap showing rating patterns"""
        if self.df is None:
            return None
        
        # Create synthetic monthly data based on review order
        clean_df = self.df.dropna(subset=['stars']).reset_index(drop=True)
        
        # Group into months (simulate)
        month_size = max(1, len(clean_df) // 12)
        monthly_data = []
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for i, month in enumerate(months):
            start_idx = i * month_size
            end_idx = min((i + 1) * month_size, len(clean_df))
            
            if start_idx < len(clean_df):
                month_reviews = clean_df.iloc[start_idx:end_idx]
                if not month_reviews.empty:
                    for rating in [1, 2, 3, 4, 5]:
                        count = len(month_reviews[month_reviews['stars'] == rating])
                        monthly_data.append({
                            'Month': month,
                            'Rating': f"{rating} Star",
                            'Count': count
                        })
        
        if not monthly_data:
            return None
        
        df_monthly = pd.DataFrame(monthly_data)
        pivot_df = df_monthly.pivot(index='Rating', columns='Month', values='Count').fillna(0)
        
        fig = px.imshow(
            pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            title=f"Rating Distribution Heatmap - {self.business_name}",
            labels={'x': 'Month', 'y': 'Rating', 'color': 'Review Count'},
            color_continuous_scale='RdYlGn'
        )
        
        return fig
    
    def get_top_keywords_by_sentiment(self):
        """Get top keywords for positive and negative reviews"""
        if self.df is None:
            return None, None
        
        # Positive reviews (4-5 stars)
        positive_reviews = self.df[self.df['stars'] >= 4]['text'].dropna().astype(str)
        positive_text = ' '.join(positive_reviews)
        positive_words = re.findall(r'\b[a-zA-Z]{3,}\b', positive_text.lower())
        
        # Negative reviews (1-2 stars)
        negative_reviews = self.df[self.df['stars'] <= 2]['text'].dropna().astype(str)
        negative_text = ' '.join(negative_reviews)
        negative_words = re.findall(r'\b[a-zA-Z]{3,}\b', negative_text.lower())
        
        # Remove stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use', 'very', 'good', 'great', 'bad', 'really', 'much', 'well', 'also', 'just', 'like', 'would', 'time', 'place', 'food', 'service'}
        
        positive_words = [word for word in positive_words if word not in stop_words]
        negative_words = [word for word in negative_words if word not in stop_words]
        
        # Count words
        positive_counts = Counter(positive_words).most_common(10)
        negative_counts = Counter(negative_words).most_common(10)
        
        # Create charts
        pos_fig = None
        neg_fig = None
        
        if positive_counts:
            pos_words, pos_counts_vals = zip(*positive_counts)
            pos_fig = px.bar(
                x=list(pos_counts_vals),
                y=list(pos_words),
                orientation='h',
                title="Top Keywords in Positive Reviews",
                labels={'x': 'Frequency', 'y': 'Keywords'},
                color=list(pos_counts_vals),
                color_continuous_scale='Greens'
            )
            pos_fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        
        if negative_counts:
            neg_words, neg_counts_vals = zip(*negative_counts)
            neg_fig = px.bar(
                x=list(neg_counts_vals),
                y=list(neg_words),
                orientation='h',
                title="Top Keywords in Negative Reviews",
                labels={'x': 'Frequency', 'y': 'Keywords'},
                color=list(neg_counts_vals),
                color_continuous_scale='Reds'
            )
            neg_fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        
        return pos_fig, neg_fig