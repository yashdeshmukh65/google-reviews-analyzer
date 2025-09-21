"""
Enhanced Google Maps Review Scraper using Selenium + Crawl4AI
Combines Selenium for browser automation with Crawl4AI for intelligent content extraction
"""

import asyncio
import json
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from crawl4ai import AsyncWebCrawler
import re

class Crawl4AIScraper:
    def __init__(self):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
    
    def log(self, message):
        """Add debug message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        self.debug_messages.append(log_msg)
        print(log_msg)
    
    def setup_chrome_driver(self):
        """Setup Chrome driver with anti-detection options"""
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    async def scrape_reviews(self, url, max_reviews=100):
        """Main scraping method combining Selenium + Crawl4AI"""
        self.log(f"🚀 Starting scrape for: {url}")
        self.log(f"📊 Target: {max_reviews} reviews")
        
        driver = None
        try:
            # Step 1: Use Selenium to load and scroll the page
            driver = self.setup_chrome_driver()
            self.log("🌐 Chrome driver initialized")
            
            driver.get(url)
            time.sleep(3)
            
            # Extract business name
            try:
                business_name_elem = driver.find_element(By.CSS_SELECTOR, "h1")
                business_name = business_name_elem.text.strip()
                self.business_info = {
                    'name': business_name,
                    'url': url,
                    'scraped_at': datetime.now().isoformat()
                }
                self.log(f"🏢 Business: {business_name}")
            except:
                self.business_info = {
                    'name': 'Unknown Business',
                    'url': url,
                    'scraped_at': datetime.now().isoformat()
                }
            
            # Look for reviews section and scroll
            self.log("🔍 Looking for reviews section...")
            
            # Try to find and click reviews tab
            try:
                reviews_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-tab-index="1"]'))
                )
                reviews_tab.click()
                time.sleep(2)
                self.log("✅ Clicked reviews tab")
            except:
                self.log("⚠️ Reviews tab not found, continuing...")
            
            # Scroll to load reviews
            self.log("📜 Scrolling to load reviews...")
            for scroll in range(10):  # Scroll up to 10 times
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
                
                # Check if we have enough reviews
                review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-review-id], .jftiEf, .MyEned')
                self.log(f"   Scroll {scroll+1}: Found {len(review_elements)} review elements")
                
                if len(review_elements) >= max_reviews or len(review_elements) > 50:
                    break
            
            # Step 2: Get page HTML and use Crawl4AI for intelligent extraction
            page_html = driver.page_source
            current_url = driver.current_url
            
            # Close Selenium driver
            driver.quit()
            driver = None
            
            # Step 3: Use Crawl4AI for intelligent content extraction
            self.log("🤖 Using Crawl4AI for intelligent extraction...")
            
            async with AsyncWebCrawler(verbose=True) as crawler:
                # Create extraction schema for reviews
                extraction_schema = {
                    "type": "object",
                    "properties": {
                        "reviews": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "reviewer_name": {"type": "string"},
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "review_text": {"type": "string"},
                                    "review_date": {"type": "string"}
                                },
                                "required": ["reviewer_name", "rating", "review_text", "review_date"]
                            }
                        },
                        "business_name": {"type": "string"}
                    }
                }
                
                # Use Crawl4AI to extract structured data
                result = await crawler.arun(
                    url=current_url,
                    html=page_html,
                    extraction_schema=extraction_schema,
                    instruction="Extract all Google Maps reviews with reviewer names, ratings (1-5 stars), review text, and dates. Focus on actual customer reviews, not business information."
                )
                
                if result.success and result.extracted_content:
                    try:
                        extracted_data = json.loads(result.extracted_content)
                        reviews = extracted_data.get('reviews', [])
                        
                        if reviews:
                            # Filter and clean reviews
                            cleaned_reviews = []
                            for review in reviews[:max_reviews]:
                                if (review.get('reviewer_name') and 
                                    review.get('review_text') and 
                                    len(review.get('review_text', '')) > 10):
                                    cleaned_reviews.append({
                                        'reviewer_name': review.get('reviewer_name', 'Anonymous'),
                                        'rating': int(review.get('rating', 3)),
                                        'review_text': review.get('review_text', ''),
                                        'review_date': review.get('review_date', 'Recent')
                                    })
                            
                            if cleaned_reviews:
                                self.reviews_data = cleaned_reviews
                                self.log(f"✅ Crawl4AI extracted {len(cleaned_reviews)} reviews!")
                                return cleaned_reviews
                    
                    except json.JSONDecodeError as e:
                        self.log(f"❌ JSON parsing error: {e}")
                
                # Fallback: Manual HTML parsing
                self.log("🔄 Crawl4AI extraction failed, using fallback parsing...")
                return await self.fallback_html_parsing(page_html)
        
        except Exception as e:
            self.log(f"❌ Scraping error: {e}")
            return []
        
        finally:
            if driver:
                driver.quit()
                self.log("🔒 Chrome driver closed")
    
    async def fallback_html_parsing(self, html_content):
        """Fallback method to parse HTML manually"""
        try:
            self.log("🔧 Using fallback HTML parsing...")
            
            # Simple regex patterns to extract review data
            reviews = []
            
            # Pattern for reviewer names (simplified)
            name_pattern = r'<span[^>]*class="[^"]*d4r55[^"]*"[^>]*>([^<]+)</span>'
            names = re.findall(name_pattern, html_content)
            
            # Pattern for ratings (aria-label with stars)
            rating_pattern = r'aria-label="(\d+) stars?"'
            ratings = re.findall(rating_pattern, html_content)
            
            # Pattern for review text (simplified)
            text_pattern = r'<span[^>]*class="[^"]*wiI7pd[^"]*"[^>]*>([^<]+)</span>'
            texts = re.findall(text_pattern, html_content)
            
            # Create reviews from extracted data
            min_length = min(len(names), len(ratings), len(texts))
            
            for i in range(min_length):
                if len(texts[i]) > 10:  # Filter out short/empty reviews
                    reviews.append({
                        'reviewer_name': names[i] if i < len(names) else f"Reviewer_{i+1}",
                        'rating': int(ratings[i]) if i < len(ratings) and ratings[i].isdigit() else 4,
                        'review_text': texts[i] if i < len(texts) else f"Review content {i+1}",
                        'review_date': 'Recent'
                    })
            
            if reviews:
                self.reviews_data = reviews[:50]  # Limit to 50 reviews
                self.log(f"✅ Fallback parsing extracted {len(self.reviews_data)} reviews")
                return self.reviews_data
            
        except Exception as e:
            self.log(f"❌ Fallback parsing error: {e}")
        
        return []
    

    
    def clear_data(self):
        """Clear all scraper data"""
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
        self.log("🧹 Cleared all scraper data")
    
    def get_debug_log(self):
        """Get debug messages as string"""
        return "\n".join(self.debug_messages)

# Create global instance
crawl4ai_scraper = Crawl4AIScraper()