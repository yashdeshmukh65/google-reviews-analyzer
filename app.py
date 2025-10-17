import streamlit as st
import pandas as pd
from src.csv_analyzer import CSVReviewAnalyzer
# Import scraper based on environment
# Force Render scraper for testing (uncomment next 3 lines)
# from src.render_scraper import render_scraper as scraper
# SCRAPER_TYPE = "render"
# print("🧪 TESTING: Using Render scraper locally")

# Normal auto-detection (comment out when testing Render scraper)
try:
    # Try Render scraper first
    from src.render_scraper import render_scraper as scraper
    SCRAPER_TYPE = "render"
except ImportError:
    try:
        # Fallback to working scraper for local
        from src.working_scraper import working_scraper as scraper
        SCRAPER_TYPE = "local"
    except ImportError:
        scraper = None
        SCRAPER_TYPE = "none"
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
    
    # Instructions for scraping process
    with st.expander("📝 How to Get Google Maps URL"):
        st.markdown("""
        **Step-by-step instructions:**
        
        1. 🔍 **Search on Google Maps**: Go to [maps.google.com](https://maps.google.com) and search for the business
        2. 🏢 **Select the Business**: Click on the business from search results
        3. 🔗 **Copy URL**: Copy the URL from your browser's address bar
        4. 📋 **Paste Here**: Paste the URL in the input field below
        
        **Example URL format:**
        ```
        https://www.google.com/maps/place/Restaurant+Name/@lat,lng,zoom/data=...
        ```
        
        **⚠️ Important Notes:**
        - Make sure the business has reviews visible on Google Maps
        - The scraping process may take 2-5 minutes depending on review count
        - Higher review counts will take longer to process
        - Chrome will automatically open, navigate to Reviews tab, and scroll through reviews
        - If scraping fails, try a different business URL or check your internet connection
        """)
    
    # Initialize analyzer and scraper
    analyzer = init_scraper_analyzer()
    # scraper already imported above
    
    # Clear data button
    if st.button("🆕 New Analysis", type="secondary"):
        # Clear scraper-specific session state
        if 'scraper_analyzer' in st.session_state:
            del st.session_state['scraper_analyzer']
        st.session_state.scraper_analyzer = CSVReviewAnalyzer()
        analyzer = st.session_state.scraper_analyzer
        scraper.clear_data()
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
            min_value=50,
            max_value=500,
            value=100,
            step=25
        )
    
    # Scrape button
    if st.button("🚀 Scrape Reviews", type="primary", use_container_width=True):
        if google_maps_url:
            # Clear analyzer data before scraping
            analyzer.df = None
            analyzer.business_name = ""
            scraper.clear_data()
            
            # Show scraping process info
            st.info("🔄 **Scraping Process Started**\n\n🔍 Finding Reviews tab...\n📜 Loading reviews by scrolling...\n📋 Extracting review data...\n\n⏳ Please wait, this may take 2-5 minutes...")
            
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
    
    # Display everything only if data is loaded
    if analyzer.df is not None and not analyzer.df.empty and 'rating' in analyzer.df.columns:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Analytics Summary with container
        with st.container():
            st.markdown("### 📊 Analytics Summary")
            st.markdown("<div style='padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
            display_analytics(analyzer)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # AI Chat Section with container
        with st.container():
            st.markdown("### 🤖 Ask AI About Your Reviews")
            st.markdown("<div style='padding: 20px; background-color: #f0f8ff; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
        
        # Sample questions
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
                if st.button(question, key=f"scraper_q_{i}", use_container_width=True):
                    st.session_state.scraper_user_question = question
        
        st.divider()
        
        # Chat interface
        user_question = st.text_area(
            "💬 Ask anything about your reviews:",
            value=st.session_state.get('scraper_user_question', ''),
            placeholder="Type your question here...",
            height=100,
            key="scraper_question_input"
        )
        
        if st.button("🚀 Ask AI", type="primary", use_container_width=True, key="scraper_ask_ai"):
            if user_question:
                with st.spinner("🧠 AI is analyzing your reviews..."):
                    response = analyzer.ask_question(user_question)
                    st.markdown("---")
                    st.markdown("### 🎯 AI Response:")
                    st.markdown(response)
            else:
                st.warning("Please enter a question first!")
        
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Visualizations with container
        with st.container():
            st.markdown("### 📊 Review Analytics & Visualizations")
            st.markdown("<div style='padding: 20px; background-color: #f9f9f9; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
        
            # Basic Charts with spacing
            st.markdown("#### Core Analytics")
            col1, col2 = st.columns(2, gap="large")
            with col1:
                fig1 = analyzer.get_rating_distribution()
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = analyzer.get_sentiment_pie()
                if fig2:
                    st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
            # Advanced Visualizations with spacing
            st.markdown("#### Detailed Analysis")
            col3, col4 = st.columns(2, gap="large")
            with col3:
                fig_sentiment = analyzer.get_sentiment_by_rating()
                if fig_sentiment:
                    st.plotly_chart(fig_sentiment, use_container_width=True)
            
            with col4:
                fig_length = analyzer.get_review_length_distribution()
                if fig_length:
                    st.plotly_chart(fig_length, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
            # Word Clouds Section with spacing
            st.markdown("#### ☁️ Word Clouds")
            wc_col1, wc_col2, wc_col3 = st.columns(3, gap="medium")
        
        with wc_col1:
            if st.button("All Reviews", key="scraper_wc_all", use_container_width=True):
                st.session_state.scraper_wordcloud_type = "all"
        with wc_col2:
            if st.button("Positive Reviews", key="scraper_wc_pos", use_container_width=True):
                st.session_state.scraper_wordcloud_type = "positive"
        with wc_col3:
            if st.button("Negative Reviews", key="scraper_wc_neg", use_container_width=True):
                st.session_state.scraper_wordcloud_type = "negative"
        
        # Display selected word cloud
        if 'scraper_wordcloud_type' in st.session_state:
            wc_fig = analyzer.get_word_cloud_figure(st.session_state.scraper_wordcloud_type)
            if wc_fig:
                if hasattr(wc_fig, 'update_layout'):  # Plotly figure
                    st.plotly_chart(wc_fig, use_container_width=True)
                else:  # Matplotlib figure
                    st.pyplot(wc_fig, use_container_width=True)
            else:
                st.info("⚠️ No text data available for word cloud generation")
        
            st.markdown("<br>", unsafe_allow_html=True)
            
            # More Advanced Charts with spacing
            st.markdown("#### Trend Analysis")
            col5, col6 = st.columns(2, gap="large")
            with col5:
                fig_scatter = analyzer.get_rating_vs_length_scatter()
                if fig_scatter:
                    st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col6:
                fig_trend = analyzer.get_trend_forecast_chart()
                if fig_trend:
                    st.plotly_chart(fig_trend, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
            # Keyword Analysis with spacing
            st.markdown("#### 🔍 Keyword Analysis")
            pos_keywords, neg_keywords = analyzer.get_top_keywords_by_sentiment()
            
            kw_col1, kw_col2 = st.columns(2, gap="large")
            with kw_col1:
                if pos_keywords:
                    st.plotly_chart(pos_keywords, use_container_width=True)
            
            with kw_col2:
                if neg_keywords:
                    st.plotly_chart(neg_keywords, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        
            # Additional Analysis
            st.markdown("#### Additional Insights")
            
            # Heatmap
            fig_heatmap = analyzer.get_monthly_trend_heatmap()
            if fig_heatmap:
                st.plotly_chart(fig_heatmap, use_container_width=True)
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Customer Behavior Analysis
            fig_behavior = analyzer.get_customer_behavior_analysis()
            if fig_behavior:
                st.plotly_chart(fig_behavior, use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # AI Insights with container
        with st.container():
            st.markdown("### 🧠 AI Insights & Actions")
            st.markdown("<div style='padding: 20px; background-color: #fff8dc; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
            col5, col6, col7 = st.columns([1, 1, 1], gap="medium")
        
        with col5:
            if st.button("🤖 Get AI Insights", use_container_width=True, key="scraper_insights"):
                with st.spinner("🧠 AI analyzing reviews..."):
                    insights = analyzer.get_insights()
                    st.session_state.scraper_insights_data = insights
        
        with col6:
            if st.button("🔮 Predictive Analysis", use_container_width=True, key="scraper_predictions"):
                with st.spinner("🔮 AI predicting trends..."):
                    predictions = analyzer.get_predictive_insights()
                    st.session_state.scraper_predictions_data = predictions
        
        with col7:
            if st.button("📋 View Raw Data", use_container_width=True, key="scraper_raw_data"):
                st.session_state.scraper_show_data = True
        
        # Show insights
        if 'scraper_insights_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 🤖 AI Business Insights:")
            st.markdown(st.session_state.scraper_insights_data)
        
        if 'scraper_predictions_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 🔮 Predictive Analysis:")
            st.markdown(st.session_state.scraper_predictions_data)
        
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Show raw data with container
        if st.session_state.get('scraper_show_data', False):
            st.markdown("<br>", unsafe_allow_html=True)
            with st.container():
                st.markdown("### 📋 Raw Review Data")
                st.markdown("<div style='padding: 20px; background-color: #f5f5f5; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
                
                display_columns = ['reviewer_name', 'shop_name', 'review_date', 'rating', 'review_text']
                available_columns = [col for col in display_columns if col in analyzer.df.columns]
                
                if available_columns:
                    display_df = analyzer.df[available_columns].copy()
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
                
                st.markdown("</div>", unsafe_allow_html=True)

def csv_upload_tab():
    """CSV Upload Tab"""
    st.header("📁 CSV Upload")
    st.markdown("Upload a CSV file containing review data")
    
    # Initialize CSV analyzer
    analyzer = init_csv_analyzer()
    
    # Clear data button
    if st.button("🆕 New Analysis", type="secondary", key="csv_new_analysis"):
        if 'csv_analyzer' in st.session_state:
            del st.session_state['csv_analyzer']
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
                
                # Display everything for CSV
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Analytics Summary with container
                with st.container():
                    st.markdown("### 📊 Analytics Summary")
                    st.markdown("<div style='padding: 20px; background-color: #f8f9fa; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
                    display_analytics(analyzer)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # AI Chat Section with container
                with st.container():
                    st.markdown("### 🤖 Ask AI About Your Reviews")
                    st.markdown("<div style='padding: 20px; background-color: #f0f8ff; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
                
                # Sample questions
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
                        if st.button(question, key=f"csv_q_{i}", use_container_width=True):
                            st.session_state.csv_user_question = question
                
                st.divider()
                
                # Chat interface
                user_question = st.text_area(
                    "💬 Ask anything about your reviews:",
                    value=st.session_state.get('csv_user_question', ''),
                    placeholder="Type your question here...",
                    height=100,
                    key="csv_question_input"
                )
                
                if st.button("🚀 Ask AI", type="primary", use_container_width=True, key="csv_ask_ai"):
                    if user_question:
                        with st.spinner("🧠 AI is analyzing your reviews..."):
                            response = analyzer.ask_question(user_question)
                            st.markdown("---")
                            st.markdown("### 🎯 AI Response:")
                            st.markdown(response)
                    else:
                        st.warning("Please enter a question first!")
                
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # Visualizations with container
                with st.container():
                    st.markdown("### 📊 Review Analytics & Visualizations")
                    st.markdown("<div style='padding: 20px; background-color: #f9f9f9; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
                
                    # Basic Charts with spacing
                    st.markdown("#### Core Analytics")
                    col1, col2 = st.columns(2, gap="large")
                    with col1:
                        fig1 = analyzer.get_rating_distribution()
                        if fig1:
                            st.plotly_chart(fig1, use_container_width=True)
                    
                    with col2:
                        fig2 = analyzer.get_sentiment_pie()
                        if fig2:
                            st.plotly_chart(fig2, use_container_width=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                
                # Advanced Visualizations
                col3, col4 = st.columns(2)
                with col3:
                    fig_sentiment = analyzer.get_sentiment_by_rating()
                    if fig_sentiment:
                        st.plotly_chart(fig_sentiment, use_container_width=True)
                
                with col4:
                    fig_length = analyzer.get_review_length_distribution()
                    if fig_length:
                        st.plotly_chart(fig_length, use_container_width=True)
                
                # Word Clouds Section
                st.subheader("☁️ Word Clouds")
                wc_col1, wc_col2, wc_col3 = st.columns(3)
                
                with wc_col1:
                    if st.button("All Reviews", key="csv_wc_all", use_container_width=True):
                        st.session_state.csv_wordcloud_type = "all"
                with wc_col2:
                    if st.button("Positive Reviews", key="csv_wc_pos", use_container_width=True):
                        st.session_state.csv_wordcloud_type = "positive"
                with wc_col3:
                    if st.button("Negative Reviews", key="csv_wc_neg", use_container_width=True):
                        st.session_state.csv_wordcloud_type = "negative"
                
                # Display selected word cloud
                if 'csv_wordcloud_type' in st.session_state:
                    wc_fig = analyzer.get_word_cloud_figure(st.session_state.csv_wordcloud_type)
                    if wc_fig:
                        if hasattr(wc_fig, 'update_layout'):  # Plotly figure
                            st.plotly_chart(wc_fig, use_container_width=True)
                        else:  # Matplotlib figure
                            st.pyplot(wc_fig, use_container_width=True)
                    else:
                        st.info("⚠️ No text data available for word cloud generation")
                
                # More Advanced Charts
                col5, col6 = st.columns(2)
                with col5:
                    fig_scatter = analyzer.get_rating_vs_length_scatter()
                    if fig_scatter:
                        st.plotly_chart(fig_scatter, use_container_width=True)
                
                with col6:
                    fig_trend = analyzer.get_trend_forecast_chart()
                    if fig_trend:
                        st.plotly_chart(fig_trend, use_container_width=True)
                
                # Keyword Analysis
                st.subheader("🔍 Keyword Analysis")
                pos_keywords, neg_keywords = analyzer.get_top_keywords_by_sentiment()
                
                kw_col1, kw_col2 = st.columns(2)
                with kw_col1:
                    if pos_keywords:
                        st.plotly_chart(pos_keywords, use_container_width=True)
                
                with kw_col2:
                    if neg_keywords:
                        st.plotly_chart(neg_keywords, use_container_width=True)
                
                # Heatmap
                fig_heatmap = analyzer.get_monthly_trend_heatmap()
                if fig_heatmap:
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Customer Behavior Analysis
                fig_behavior = analyzer.get_customer_behavior_analysis()
                if fig_behavior:
                    st.plotly_chart(fig_behavior, use_container_width=True)
                
                    st.markdown("</div>", unsafe_allow_html=True)
                
                st.markdown("<br><br>", unsafe_allow_html=True)
                
                # AI Insights with container
                with st.container():
                    st.markdown("### 🧠 AI Insights & Actions")
                    st.markdown("<div style='padding: 20px; background-color: #fff8dc; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
                    col5, col6, col7 = st.columns([1, 1, 1], gap="medium")
                
                with col5:
                    if st.button("🤖 Get AI Insights", use_container_width=True, key="csv_insights"):
                        with st.spinner("🧠 AI analyzing reviews..."):
                            insights = analyzer.get_insights()
                            st.session_state.csv_insights_data = insights
                
                with col6:
                    if st.button("🔮 Predictive Analysis", use_container_width=True, key="csv_predictions"):
                        with st.spinner("🔮 AI predicting trends..."):
                            predictions = analyzer.get_predictive_insights()
                            st.session_state.csv_predictions_data = predictions
                
                with col7:
                    if st.button("📋 View Raw Data", use_container_width=True, key="csv_raw_data"):
                        st.session_state.csv_show_data = True
                
                # Show insights
                if 'csv_insights_data' in st.session_state:
                    st.markdown("---")
                    st.markdown("### 🤖 AI Business Insights:")
                    st.markdown(st.session_state.csv_insights_data)
                
                if 'csv_predictions_data' in st.session_state:
                    st.markdown("---")
                    st.markdown("### 🔮 Predictive Analysis:")
                    st.markdown(st.session_state.csv_predictions_data)
                
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # Show raw data with container
                if st.session_state.get('csv_show_data', False):
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.container():
                        st.markdown("### 📋 Raw Review Data")
                        st.markdown("<div style='padding: 20px; background-color: #f5f5f5; border-radius: 10px; margin: 10px 0;'>", unsafe_allow_html=True)
                        
                        display_columns = ['reviewer_name', 'shop_name', 'review_date', 'rating', 'review_text']
                        available_columns = [col for col in display_columns if col in analyzer.df.columns]
                        
                        if available_columns:
                            display_df = analyzer.df[available_columns].copy()
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
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                
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

if __name__ == "__main__":
    # Check for Gemini API key from environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        st.error("❌ Please set your GEMINI_API_KEY environment variable")
        st.info("For local development, add GEMINI_API_KEY to your .env file")
        st.info("For Render deployment, set GEMINI_API_KEY in environment variables")
        st.stop()
    
    # Display scraper type for debugging
    if SCRAPER_TYPE == "render":
        st.sidebar.success("🚀 Running on Render (Headless)")
    elif SCRAPER_TYPE == "local":
        st.sidebar.info("💻 Running Locally")
    else:
        st.sidebar.error("❌ No scraper available")
    
    # Initialize session state
    if 'scraper_user_question' not in st.session_state:
        st.session_state.scraper_user_question = ''
    if 'csv_user_question' not in st.session_state:
        st.session_state.csv_user_question = ''
    if 'scraper_show_data' not in st.session_state:
        st.session_state.scraper_show_data = False
    if 'csv_show_data' not in st.session_state:
        st.session_state.csv_show_data = False
    if 'scraper_wordcloud_type' not in st.session_state:
        st.session_state.scraper_wordcloud_type = 'all'
    if 'csv_wordcloud_type' not in st.session_state:
        st.session_state.csv_wordcloud_type = 'all'
    
    main()