import streamlit as st
import pandas as pd
from src.csv_analyzer import CSVReviewAnalyzer
from src.real_time_scraper import real_time_scraper
import asyncio
import os
import json

# Page config
st.set_page_config(
    page_title="Google Review Analyser",
    page_icon="⭐",
    layout="wide"
)

# Initialize separate analyzers for each tab
def init_scraper_analyzer():
    if 'scraper_analyzer' not in st.session_state:
        st.session_state.scraper_analyzer = CSVReviewAnalyzer()
    return st.session_state.scraper_analyzer

def init_csv_analyzer():
    if 'csv_analyzer' not in st.session_state:
        st.session_state.csv_analyzer = CSVReviewAnalyzer()
    return st.session_state.csv_analyzer

def display_analytics(analyzer):
    """Display analytics summary"""
    if analyzer.df is not None and not analyzer.df.empty:
        try:
            # Check if required columns exist
            if 'rating' not in analyzer.df.columns:
                st.warning("⚠️ Data format issue: 'rating' column not found")
                return
            
            col1, col2, col3, col4 = st.columns(4)
            
            total_reviews = len(analyzer.df)
            avg_rating = analyzer.df['rating'].mean()
            positive_count = len(analyzer.df[analyzer.df['rating'] >= 4])
            negative_count = len(analyzer.df[analyzer.df['rating'] <= 2])
            
            with col1:
                st.metric("Total Reviews", total_reviews)
            with col2:
                st.metric("Average Rating", f"{avg_rating:.1f}⭐")
            with col3:
                st.metric("Positive Reviews", f"{positive_count} ({positive_count/total_reviews*100:.1f}%)")
            with col4:
                st.metric("Negative Reviews", f"{negative_count} ({negative_count/total_reviews*100:.1f}%)")
        except Exception as e:
            st.error(f"❌ Error displaying analytics: {e}")
            st.info("Please clear data and try again.")



def scraper_tab():
    """Internal Scraper Tab"""
    st.header("🌐 Internal Scraper")
    st.markdown("Scrape reviews directly from Google Maps business pages")
    
    # Initialize analyzer and scraper
    analyzer = init_scraper_analyzer()
    scraper = real_time_scraper
    
    # Clear data button
    if st.button("🆕 New Analysis", type="secondary"):
        # Clear all session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Reinitialize analyzer
        st.session_state.analyzer = CSVReviewAnalyzer()
        analyzer = st.session_state.analyzer
        # Clear scraper data
        scraper.clear_data()
        # Delete saved data file
        try:
            if os.path.exists('data/reviews_data.json'):
                os.remove('data/reviews_data.json')
        except:
            pass
        st.success("🧹 Cleared all data - ready for new analysis!")
        st.rerun()
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        google_maps_url = st.text_input(
            "Google Maps Business URL",
            placeholder="https://maps.google.com/...",
            help="Enter the Google Maps URL of the business you want to analyze"
        )
    
    with col2:
        max_reviews = st.number_input(
            "Max Reviews",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )
    
    # Scrape button
    if st.button("🚀 Scrape Reviews", type="primary", use_container_width=True):
        if google_maps_url:
            # Clear analyzer data before scraping
            analyzer.df = None
            analyzer.business_name = ""
            scraper.clear_data()
            
            with st.spinner(f"Scraping up to {max_reviews} reviews... This may take a few minutes."):
                try:
                    # Run scraper
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    reviews = loop.run_until_complete(
                        scraper.scrape_reviews(google_maps_url, max_reviews)
                    )
                    
                    if reviews:
                        st.success(f"✅ Successfully scraped {len(reviews)} REAL reviews!")
                        # Load data into analyzer
                        analyzer.load_json_data(reviews, scraper.business_info)
                        st.rerun()
                    else:
                        st.error("❌ Failed to scrape reviews. Please check the URL and try again.")
                        
                        # Show debug information
                        with st.expander("🔍 Debug Information"):
                            debug_log = scraper.get_debug_log()
                            st.text(debug_log)
                        
                except Exception as e:
                    st.error(f"❌ Error during scraping: {str(e)}")
                    
                    # Show debug information on error
                    with st.expander("🔍 Debug Information"):
                        debug_log = scraper.get_debug_log()
                        st.text(debug_log)
        else:
            st.warning("Please enter a Google Maps URL")
    
    # No automatic data loading - only show after active scraping
    
    # Display analytics only if data is actively loaded in current session
    if analyzer.df is not None and not analyzer.df.empty and 'rating' in analyzer.df.columns:
        st.divider()
        st.subheader("📊 Analytics Summary")
        display_analytics(analyzer)

def csv_upload_tab():
    """CSV Upload Tab"""
    st.header("📁 CSV Upload")
    st.markdown("Upload a CSV file containing review data")
    
    # Initialize CSV analyzer for this tab only
    analyzer = init_csv_analyzer()
    
    # Clear data button for CSV tab
    if st.button("🆕 New Analysis", type="secondary", key="csv_new_analysis"):
        # Clear CSV-specific session state
        if 'csv_analyzer' in st.session_state:
            del st.session_state['csv_analyzer']
        # Reinitialize CSV analyzer
        st.session_state.csv_analyzer = CSVReviewAnalyzer()
        analyzer = st.session_state.csv_analyzer
        st.success("🧹 Cleared all data - ready for new CSV upload!")
        st.rerun()
    
    # CSV format example
    with st.expander("📋 Expected CSV Format"):
        st.markdown("""
        Your CSV file should have these columns:
        - **title**: Name of shop/business
        - **url**: Business URL
        - **stars**: Rating (1-5)
        - **name**: Reviewer name
        - **reviewUrl**: Review URL (optional)
        - **text**: Review feedback/content
        
        Example:
        ```
        title,url,stars,name,reviewUrl,text
        Pizza Palace,https://maps.google.com/...,5,John Doe,,Great service and food!
        Coffee Shop,https://maps.google.com/...,4,Jane Smith,,Good experience overall
        ```
        """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload your reviews CSV file"
    )
    
    if uploaded_file is not None:
        try:
            # Read CSV file
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = ['title', 'stars', 'name', 'text']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing required columns: {', '.join(missing_columns)}")
                st.info("Please ensure your CSV has the required columns as shown in the format example above.")
            else:
                # Map columns to expected format
                df_mapped = df.copy()
                df_mapped['reviewer_name'] = df['name']
                df_mapped['shop_name'] = df['title']
                df_mapped['rating'] = df['stars']
                df_mapped['review_text'] = df['text']
                df_mapped['review_date'] = df.get('reviewUrl', 'Recent')
                
                # Load data into analyzer
                analyzer.df = df_mapped
                analyzer.business_name = df['title'].iloc[0] if len(df) > 0 else "CSV Upload"
                
                st.success(f"✅ Successfully loaded {len(df)} reviews from CSV!")
                
                # Display analytics only
                st.divider()
                st.subheader("📊 Analytics Summary")
                display_analytics(analyzer)
                
        except Exception as e:
            st.error(f"❌ Error reading CSV file: {str(e)}")
            st.info("Please make sure your CSV file is properly formatted.")

def main():
    st.title("🌐 Google Reviews Analyser")
    st.markdown("Analyze reviews using our internal scraper or upload your own CSV data")
    
    # Create tabs
    tab1, tab2 = st.tabs(["🌐 Internal Scraper", "📁 CSV Upload"])
    
    with tab1:
        scraper_tab()
    
    with tab2:
        csv_upload_tab()
    
    # AI Chat Section (check both analyzers)
    scraper_analyzer = init_scraper_analyzer()
    csv_analyzer = init_csv_analyzer()
    
    # Use whichever analyzer has data
    active_analyzer = None
    if scraper_analyzer.df is not None and not scraper_analyzer.df.empty and 'rating' in scraper_analyzer.df.columns:
        active_analyzer = scraper_analyzer
    elif csv_analyzer.df is not None and not csv_analyzer.df.empty and 'rating' in csv_analyzer.df.columns:
        active_analyzer = csv_analyzer
    
    if active_analyzer:
        st.divider()
        st.header("🤖 Ask AI About Your Reviews")
        
        # Sample questions as buttons
        st.subheader("💡 Quick Questions:")
        sample_questions = [
            "What are the main complaints?",
            "What do customers love most?",
            "How can we improve ratings?",
            "What are common positive themes?",
            "What issues appear most frequently?",
            "Give me actionable recommendations"
        ]
        
        cols = st.columns(3)
        for i, question in enumerate(sample_questions):
            with cols[i % 3]:
                if st.button(question, key=f"q_{i}", use_container_width=True):
                    st.session_state.user_question = question
        
        st.divider()
        
        # Chat interface
        user_question = st.text_area(
            "💬 Ask anything about your reviews:",
            value=st.session_state.get('user_question', ''),
            placeholder="Type your question here...",
            height=100
        )
        
        if st.button("🚀 Ask AI", type="primary", use_container_width=True):
            if user_question:
                with st.spinner("🧠 AI is analyzing your reviews..."):
                    response = active_analyzer.ask_question(user_question)
                    
                    st.markdown("---")
                    st.markdown("### 🎯 AI Response:")
                    st.markdown(response)
            else:
                st.warning("Please enter a question first!")
        
        # Visualizations Section
        st.divider()
        st.header("📊 Review Analytics & Visualizations")
        
        # Rating Distribution
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = active_analyzer.get_rating_distribution()
            if fig1:
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            fig2 = active_analyzer.get_sentiment_pie()
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
        
        # Rating Trend
        fig3 = active_analyzer.get_rating_trend()
        if fig3:
            st.plotly_chart(fig3, use_container_width=True)
        
        # Word Analysis
        st.subheader("🔤 Word Analysis")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.write("**Most Common Words (All Reviews)**")
            fig4 = active_analyzer.get_top_words()
            if fig4:
                st.plotly_chart(fig4, use_container_width=True)
        
        with col4:
            st.write("**Word Cloud (Positive Reviews)**")
            wordcloud = active_analyzer.get_word_cloud_data(min_rating=4, max_rating=5)
            if wordcloud:
                try:
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                except ImportError:
                    st.info("Install matplotlib and wordcloud for word cloud visualization")
            else:
                st.info("Word cloud not available - install wordcloud package")
        
        # AI Insights
        st.divider()
        col5, col6, col7 = st.columns([1, 1, 1])
        
        with col5:
            if st.button("🤖 Get AI Insights", use_container_width=True):
                with st.spinner("🧠 AI analyzing reviews..."):
                    insights = active_analyzer.get_insights()
                    st.session_state.insights = insights
        
        with col6:
            if st.button("🔮 Predictive Analysis", use_container_width=True):
                with st.spinner("🔮 AI predicting trends..."):
                    predictions = active_analyzer.get_predictive_insights()
                    st.session_state.predictions = predictions
        
        with col7:
            if st.button("📋 View Raw Data", use_container_width=True):
                st.session_state.show_data = True
        
        # Show AI insights if generated
        if 'insights' in st.session_state:
            st.markdown("---")
            st.markdown("### 🤖 AI Business Insights:")
            st.markdown(st.session_state.insights)
        
        # Show predictions if generated
        if 'predictions' in st.session_state:
            st.markdown("---")
            st.markdown("### 🔮 Predictive Analysis:")
            st.markdown(st.session_state.predictions)
        
        # Show raw data if requested - only required fields
        if st.session_state.get('show_data', False):
            st.markdown("---")
            st.markdown("### 📋 Raw Review Data:")
            
            # Create display dataframe with only required columns
            display_columns = ['reviewer_name', 'shop_name', 'review_date', 'rating', 'review_text']
            available_columns = [col for col in display_columns if col in active_analyzer.df.columns]
            
            if available_columns:
                display_df = active_analyzer.df[available_columns].copy()
                
                # Rename columns for better display
                column_names = {
                    'reviewer_name': 'Reviewer Name',
                    'shop_name': 'Shop Name', 
                    'review_date': 'Date',
                    'rating': 'Stars',
                    'review_text': 'Review Text'
                }
                
                display_df = display_df.rename(columns=column_names)
                st.dataframe(display_df, use_container_width=True)
            else:
                st.warning("⚠️ Required columns not found in data")

if __name__ == "__main__":
    # Check for Gemini API key
    if not os.getenv("GEMINI_API_KEY"):
        st.error("❌ Please set your GEMINI_API_KEY in the .env file")
        st.stop()
    
    # Initialize session state
    if 'user_question' not in st.session_state:
        st.session_state.user_question = ''
    if 'show_data' not in st.session_state:
        st.session_state.show_data = False
    
    main()