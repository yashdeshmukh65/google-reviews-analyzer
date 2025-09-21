import json
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class SimpleReviewScraper:
    def __init__(self):
        self.reviews_data = []
        self.business_info = {}
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def setup_driver(self):
        """Setup Chrome driver"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    async def scrape_reviews(self, url, max_reviews=100):
        """Simple scraping with Selenium + Gemini"""
        driver = None
        try:
            print("Starting simple scraper...")
            driver = self.setup_driver()
            
            print(f"Loading: {url}")
            driver.get(url)
            time.sleep(5)
            
            # Get business name
            try:
                business_name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                ).text
                self.business_info = {
                    'name': business_name,
                    'url': url,
                    'scraped_at': datetime.now().isoformat()
                }
                print(f"Business: {business_name}")
            except:
                self.business_info = {'name': 'Unknown', 'url': url, 'scraped_at': datetime.now().isoformat()}
            
            # Scroll to load reviews
            print("Scrolling to load reviews...")
            for i in range(10):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Click show more buttons
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, '[aria-label*="more"], .w8nwRe')
                    for btn in buttons[:3]:
                        if btn.is_displayed():
                            btn.click()
                            time.sleep(1)
                except:
                    pass
            
            # Get HTML and parse with Gemini
            html = driver.page_source
            print(f"HTML length: {len(html)}")
            
            # Parse with Gemini
            prompt = f"""
            Extract Google Maps reviews from this HTML. Return ONLY valid JSON:
            
            {{
                "reviews": [
                    {{
                        "reviewer_name": "Name",
                        "rating": 5,
                        "review_text": "Review text",
                        "review_date": "Date"
                    }}
                ]
            }}
            
            HTML (first 50000 chars):
            {html[:50000]}
            """
            
            print("Parsing with Gemini...")
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3]
                elif text.startswith('```'):
                    text = text[3:-3]
                
                data = json.loads(text)
                reviews = data.get('reviews', [])
                
                if reviews:
                    self.reviews_data = reviews
                    print(f"✅ Found {len(reviews)} reviews")
                    return reviews
                else:
                    print("❌ No reviews in response")
                    return []
            else:
                print("❌ No response from Gemini")
                return []
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
        finally:
            if driver:
                driver.quit()

# Create instance
simple_scraper = SimpleReviewScraper()