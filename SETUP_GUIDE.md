# Google Review Analyser - Setup Guide

## 🚀 Quick Start

This application provides a tabbed interface for analyzing Google Maps reviews using either:
1. **Internal Scraper**: Direct scraping from Google Maps using Selenium + Crawl4AI
2. **CSV Upload**: Upload your own review data in CSV format

## 📋 Prerequisites

- Python 3.8 or higher
- Chrome browser installed
- Internet connection for scraping

## 🛠️ Installation Steps

### 1. Clone/Download the Project
```bash
cd google_review_analyser
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Environment Variables
Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

Get your Gemini API key from: https://makersuite.google.com/app/apikey

### 4. Run the Application
```bash
streamlit run app.py
```

## 📊 Features

### Tab 1: Internal Scraper
- **Input**: Google Maps business URL
- **Process**: Selenium opens the page, scrolls to load reviews, Crawl4AI extracts data
- **Output**: JSON format with reviewer name, rating, review text, review time, shop name
- **Analytics**: Total reviews, average rating, positive vs negative breakdown

### Tab 2: CSV Upload
- **Input**: CSV file with review data
- **Format**: Must include columns: `reviewer_name`, `rating`, `review_text`, `review_date`
- **Output**: Same analytics as scraper tab

## 📁 Expected Data Formats

### JSON Output (from scraper):
```json
{
  "reviews": [
    {
      "reviewer_name": "John Doe",
      "rating": 5,
      "review_text": "Great service and food!",
      "review_date": "2 weeks ago"
    }
  ],
  "business_info": {
    "name": "Restaurant Name",
    "url": "https://maps.google.com/...",
    "scraped_at": "2024-01-15T10:30:00"
  }
}
```

### CSV Format (for upload):
```csv
reviewer_name,rating,review_text,review_date
John Doe,5,"Great service and delicious food!",2024-01-15
Jane Smith,4,"Good experience overall.",2024-01-14
```

## 🔧 Technical Architecture

### Backend Components:
- **Streamlit**: Web interface framework
- **Selenium**: Browser automation for page loading and scrolling
- **Crawl4AI**: Intelligent content extraction using AI
- **Google Gemini**: AI analysis and insights
- **Pandas**: Data processing and analysis
- **Plotly**: Interactive visualizations

### Scraping Process:
1. Selenium opens Chrome browser with anti-detection settings
2. Navigates to Google Maps URL and scrolls to load reviews
3. Crawl4AI analyzes the HTML content using AI
4. Extracts structured review data (name, rating, text, date)
5. Saves data in JSON format for analysis

## 🎯 Usage Instructions

### Using the Internal Scraper:
1. Go to the "Internal Scraper" tab
2. Paste a Google Maps business URL (e.g., `https://maps.google.com/...`)
3. Set maximum number of reviews to scrape (10-500)
4. Click "Scrape Reviews"
5. Wait for the process to complete (may take 2-5 minutes)
6. View analytics and reviews table

### Using CSV Upload:
1. Go to the "CSV Upload" tab
2. Prepare your CSV file with required columns
3. Click "Choose a CSV file" and select your file
4. View analytics and reviews table immediately

### AI Analysis Features:
- Ask questions about your reviews using natural language
- Get AI-powered insights and recommendations
- View interactive charts and visualizations
- Export data for further analysis

## 🚨 Important Notes

### Scraping Considerations:
- Google Maps has anti-scraping protection
- Scraping may be slow to avoid detection
- Some reviews might not be extracted due to dynamic content
- Always respect website terms of service

### Data Privacy:
- All data is processed locally
- No data is sent to external servers (except Gemini API for analysis)
- Review data is saved in local JSON files

### Troubleshooting:
- If scraping fails, check the debug information
- Ensure Chrome browser is installed and updated
- Check internet connection
- Verify the Google Maps URL is correct

## 📦 Dependencies

```
streamlit              # Web interface
google-generativeai    # Gemini AI integration
pandas                 # Data processing
python-dotenv          # Environment variables
plotly                 # Interactive charts
wordcloud              # Word cloud generation
matplotlib             # Additional plotting
selenium               # Browser automation
webdriver-manager      # Chrome driver management
crawl4ai               # AI-powered web scraping
```

## 🔄 Updates and Maintenance

- Keep dependencies updated: `pip install -r requirements.txt --upgrade`
- Update Chrome browser regularly
- Monitor Gemini API usage and limits
- Check for new versions of Crawl4AI for improved extraction

## 📞 Support

For issues or questions:
1. Check the debug information in the app
2. Verify all dependencies are installed correctly
3. Ensure environment variables are set properly
4. Check Chrome browser compatibility