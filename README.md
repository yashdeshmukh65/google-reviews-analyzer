# 🌐 Google Review Analyser

A powerful web application for analyzing Google Maps reviews using AI-powered scraping and intelligent insights.

## ✨ Features

### 🎯 Dual Interface Design
- **Tab 1: Internal Scraper** - Direct scraping from Google Maps using Selenium + Crawl4AI
- **Tab 2: CSV Upload** - Upload and analyze your own review data

### 🤖 AI-Powered Analysis
- Natural language Q&A about your reviews
- Automated insights and recommendations
- Sentiment analysis and trend forecasting
- Smart review categorization

### 📊 Rich Visualizations
- Interactive rating distributions
- Sentiment analysis charts
- Word frequency analysis
- Trend forecasting graphs
- Customer behavior insights

### 🔧 Advanced Scraping
- **Selenium**: Browser automation for dynamic content loading
- **Crawl4AI**: AI-powered content extraction
- **Anti-detection**: Smart scrolling and human-like behavior
- **Robust parsing**: Multiple fallback extraction methods

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repository
git clone <repository-url>
cd google_review_analyser

# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 2. Run the Application
```bash
streamlit run app.py
```

### 3. Test Your Setup
```bash
python test_setup.py
```

## 📋 Usage Guide

### Internal Scraper Tab
1. **Input**: Paste a Google Maps business URL
2. **Configure**: Set maximum number of reviews (10-500)
3. **Scrape**: Click "Scrape Reviews" and wait 2-5 minutes
4. **Analyze**: View analytics, ask AI questions, explore visualizations

### CSV Upload Tab
1. **Prepare**: Format your CSV with required columns:
   - `reviewer_name`: Name of the reviewer
   - `rating`: Rating (1-5)
   - `review_text`: Review content
   - `review_date`: Date of review
2. **Upload**: Select your CSV file
3. **Analyze**: Instantly view analytics and insights

## 🏗️ Technical Architecture

### Core Components
- **Frontend**: Streamlit web interface with tabbed navigation
- **Scraping Engine**: Selenium + Crawl4AI for intelligent extraction
- **AI Analysis**: Google Gemini for insights and Q&A
- **Data Processing**: Pandas for analysis and visualization
- **Visualization**: Plotly for interactive charts

### Scraping Process
```
Google Maps URL → Selenium (Load & Scroll) → Crawl4AI (Extract) → JSON Data → Analysis
```

### Data Flow
```
Input (URL/CSV) → Processing → Storage (JSON) → AI Analysis → Visualizations → Insights
```

## 📊 Data Formats

### JSON Output (Scraper)
```json
{
  "reviews": [
    {
      "reviewer_name": "John Doe",
      "rating": 5,
      "review_text": "Great service!",
      "review_date": "2 weeks ago"
    }
  ],
  "business_info": {
    "name": "Business Name",
    "url": "https://maps.google.com/...",
    "scraped_at": "2024-01-15T10:30:00"
  }
}
```

### CSV Format (Upload)
```csv
reviewer_name,rating,review_text,review_date
John Doe,5,"Great service and food!",2024-01-15
Jane Smith,4,"Good experience overall.",2024-01-14
```

## 🔍 AI Capabilities

### Question Types Supported
- **Sentiment Analysis**: "What are customers saying about service?"
- **Issue Identification**: "What are the main complaints?"
- **Improvement Suggestions**: "How can we improve our ratings?"
- **Trend Analysis**: "What patterns do you see in recent reviews?"
- **Competitive Insights**: "What do customers love most?"

### Sample Questions
- "What are the main complaints?"
- "What do customers love most?"
- "How can we improve ratings?"
- "What are common positive themes?"
- "Give me actionable recommendations"

## 📈 Analytics Features

### Summary Metrics
- Total review count
- Average rating with trend
- Positive vs negative breakdown
- Recent activity patterns

### Visualizations
- **Rating Distribution**: Bar chart of 1-5 star ratings
- **Sentiment Analysis**: Pie chart of positive/negative/neutral
- **Trend Analysis**: Time-series rating trends
- **Word Analysis**: Most common words and phrases
- **Word Clouds**: Visual representation of review themes

### Predictive Analytics
- Rating trend forecasting
- Customer behavior analysis
- Seasonal pattern detection
- Risk assessment indicators

## 🛠️ Dependencies

```
streamlit>=1.28.0          # Web interface framework
google-generativeai>=0.3.0 # Gemini AI integration
pandas>=1.5.0              # Data processing
selenium>=4.15.0           # Browser automation
crawl4ai>=0.2.0           # AI-powered web scraping
plotly>=5.15.0            # Interactive visualizations
webdriver-manager>=4.0.0   # Chrome driver management
python-dotenv>=1.0.0       # Environment variables
wordcloud>=1.9.0          # Word cloud generation
matplotlib>=3.7.0         # Additional plotting
```

## ⚠️ Important Notes

### Scraping Considerations
- **Rate Limiting**: Scraping includes delays to avoid detection
- **Success Rate**: May vary based on Google's anti-bot measures
- **Data Quality**: Some reviews might not extract perfectly
- **Legal Compliance**: Always respect website terms of service

### Performance Tips
- Start with smaller review counts (50-100) for testing
- Use CSV upload for large datasets when possible
- Monitor API usage for Gemini integration
- Keep Chrome browser updated for best compatibility

### Privacy & Security
- All processing happens locally
- Review data stored in local JSON files
- Only AI analysis queries sent to Gemini API
- No personal data transmitted externally

## 🔧 Troubleshooting

### Common Issues
1. **Scraping Fails**: Check URL format, internet connection, Chrome installation
2. **No Reviews Found**: Try different URL format or smaller review count
3. **AI Analysis Errors**: Verify Gemini API key in .env file
4. **CSV Upload Issues**: Check column names and data format

### Debug Information
- Enable debug mode in scraper for detailed logs
- Check browser console for JavaScript errors
- Verify all dependencies are correctly installed
- Test with sample data first

## 🚀 Future Enhancements

- [ ] Multi-language support for international reviews
- [ ] Batch processing for multiple businesses
- [ ] Advanced filtering and search capabilities
- [ ] Export functionality for reports
- [ ] Integration with other review platforms
- [ ] Real-time monitoring and alerts
- [ ] Custom AI model training

## 📞 Support

For issues, questions, or contributions:
1. Check the troubleshooting section
2. Run the test setup script
3. Review debug logs in the application
4. Ensure all dependencies are up to date

## 📄 License

This project is for educational and research purposes. Please respect website terms of service and applicable laws when scraping data.

---

**Built with ❤️ using Streamlit, Selenium, Crawl4AI, and Google Gemini**