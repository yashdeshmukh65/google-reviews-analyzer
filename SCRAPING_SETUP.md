# 🚀 Direct Scraping Setup Guide

## 🔧 **Setup Instructions**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. API Keys Setup**
Add to your `.env` file:
```
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
```

**Get API Keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Gemini**: https://makersuite.google.com/app/apikey

### **3. Chrome Browser**
- Ensure Chrome browser is installed
- WebDriver will be auto-downloaded by webdriver-manager

### **4. Run the App**
```bash
streamlit run app.py
```

## 🎯 **How It Works**

### **New Workflow:**
1. **Enter Google Maps URL** → Business page URL
2. **Set Max Reviews** → How many reviews to scrape (10-500)
3. **Click "Scrape Reviews"** → Automated scraping starts
4. **AI Analysis** → Reviews parsed and stored automatically
5. **Instant Display** → UI updates with scraped data

### **No More CSV Upload!**
- ❌ No external scraping needed
- ❌ No CSV file downloads
- ❌ No manual uploads
- ✅ Direct scraping integration
- ✅ Automatic data storage
- ✅ Real-time UI updates

## 🛡️ **Anti-Detection Features**

### **Selenium Settings:**
- **Headless Mode** - Runs in background
- **Random User Agents** - Mimics real browsers
- **Smart Delays** - Human-like timing
- **Anti-Detection Scripts** - Hides automation flags

### **Best Practices:**
- **Random Delays** - 1-5 seconds between actions
- **Gradual Scrolling** - Natural scroll patterns
- **Limit Requests** - Max 500 reviews per session
- **Rotate Sessions** - Don't scrape too frequently

## 📁 **Project Structure**

```
google_review_analyser/
├── src/
│   ├── scraper_service.py    # Selenium + Crawl4AI scraping
│   └── csv_analyzer.py       # Data analysis (updated)
├── data/
│   └── reviews_data.json     # Scraped reviews storage
├── app.py                    # Updated Streamlit UI
└── .env                      # API keys
```

## ⚡ **Features**

### **Automated Pipeline:**
1. **Selenium** → Opens Google Maps, scrolls, loads reviews
2. **HTML Extraction** → Gets raw page content
3. **LLM Parsing** → Gemini extracts structured data
4. **JSON Storage** → Saves to `data/reviews_data.json`
5. **UI Display** → Automatically shows in interface

### **Smart Scraping:**
- **Dynamic Loading** - Handles infinite scroll
- **Show More Buttons** - Clicks to expand reviews
- **Review Counting** - Stops at specified limit
- **Error Handling** - Graceful failure recovery

## 🚨 **Important Notes**

### **Rate Limiting:**
- Don't scrape the same business too frequently
- Use reasonable review limits (100-200 max)
- Add delays between different businesses

### **Legal Compliance:**
- Respect Google's Terms of Service
- Use for research/analysis purposes
- Don't overload their servers

### **Troubleshooting:**
- **Chrome Issues**: Update Chrome browser
- **WebDriver Errors**: Clear browser cache
- **API Errors**: Check API key validity
- **Timeout Issues**: Increase delays in scraper

## 🎉 **Benefits**

- **Fully Automated** - No manual steps
- **Real-time Data** - Always fresh reviews
- **Scalable** - Can scrape multiple businesses
- **Integrated** - Everything in one application
- **Professional** - Production-ready solution

Your Google Reviews Analyser now has **direct scraping capabilities**!