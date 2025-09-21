import asyncio
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
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.models import LLMConfig
import os
from dotenv import load_dotenv

load_dotenv()

class ReviewScraperService:
    def __init__(self):
        self.reviews_data = []
        self.business_info = {}
        
    def setup_selenium_driver(self):
        """Setup Chrome driver"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Chrome driver setup failed: {e}")
            return None
    
    def get_page_with_selenium(self, url):
        """Use Selenium to load page and get final URL"""
        driver = None
        try:
            driver = self.setup_selenium_driver()
            if not driver:
                return None, None
                
            print(f"Loading page with Selenium: {url}")
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
                print(f"Found business: {business_name}")
            except:
                self.business_info = {'name': 'Unknown Business', 'url': url, 'scraped_at': datetime.now().isoformat()}
            
            # Scroll to load reviews
            for i in range(5):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            final_url = driver.current_url
            print(f"Final URL after Selenium: {final_url}")
            return final_url, driver.page_source
            
        except Exception as e:
            print(f"Selenium error: {e}")
            return None, None
        finally:
            if driver:
                driver.quit()
    
    async def scrape_with_crawl4ai(self, url):
        """Use Crawl4AI with LLM extraction"""
        try:
            llm_config = LLMConfig(
                provider="gemini/gemini-1.5-flash",
                api_token=os.getenv("GEMINI_API_KEY")
            )
            
            extraction_strategy = LLMExtractionStrategy(
                llm_config=llm_config,
                instruction="""
                Extract Google Maps reviews from this page. For each review extract:
                - reviewer_name: Name of reviewer
                - rating: Star rating (1-5)
                - review_text: Full review text
                - review_date: Date of review
                
                Return as JSON array.
                """,
                schema={
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
                        }
                    }
                }
            )
            
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(
                    url=url,
                    extraction_strategy=extraction_strategy,
                    js_code="""
                    // Scroll to load more reviews
                    for(let i = 0; i < 5; i++) {
                        window.scrollTo(0, document.body.scrollHeight);
                        await new Promise(resolve => setTimeout(resolve, 2000));
                    }
                    
                    // Click show more buttons
                    const showMoreButtons = document.querySelectorAll('[aria-label*="more"], .w8nwRe');
                    for(let button of showMoreButtons) {
                        if(button.offsetParent !== null) {
                            button.click();
                            await new Promise(resolve => setTimeout(resolve, 1000));
                        }
                    }
                    """,
                    wait_for="css:.jftiEf, [data-review-id]",
                    delay_before_return_html=3
                )
                
                if result.success and result.extracted_content:
                    data = json.loads(result.extracted_content)
                    reviews = data.get('reviews', [])
                    print(f"Crawl4AI extracted {len(reviews)} reviews")
                    return reviews
                else:
                    print("Crawl4AI extraction failed")
                    return []
                    
        except Exception as e:
            print(f"Crawl4AI error: {e}")
            return []
    
    async def scrape_reviews(self, google_maps_url, max_reviews=100):
        """Main scraping method using both Selenium and Crawl4AI"""
        try:
            print("Starting hybrid scraping (Selenium + Crawl4AI)")
            
            # Method 1: Try Crawl4AI directly first
            print("Trying Crawl4AI direct approach...")
            reviews = await self.scrape_with_crawl4ai(google_maps_url)
            
            if reviews and len(reviews) > 0:
                self.reviews_data = reviews
                return reviews
            
            # Method 2: Use Selenium to get final URL, then Crawl4AI
            print("Trying Selenium + Crawl4AI approach...")
            final_url, html_content = self.get_page_with_selenium(google_maps_url)
            
            if final_url and final_url != google_maps_url:
                print(f"Using final URL from Selenium: {final_url}")
                reviews = await self.scrape_with_crawl4ai(final_url)
                
                if reviews:
                    self.reviews_data = reviews
                    return reviews
            
            # Method 3: Fallback to direct Gemini parsing of Selenium HTML
            if html_content:
                print("Trying direct Gemini parsing...")
                reviews = await self.parse_html_with_gemini(html_content)
                
                if reviews:
                    self.reviews_data = reviews
                    return reviews
            
            print("All methods failed")
            return []
            
        except Exception as e:
            print(f"Scraping error: {e}")
            return []
    
    async def parse_html_with_gemini(self, html_content):
        """Fallback: Parse HTML directly with Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Extract Google Maps reviews from this HTML. Return JSON:
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
            
            HTML (first 40000 chars):
            {html_content[:40000]}
            """
            
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            data = json.loads(response_text)
            reviews = data.get('reviews', [])
            print(f"Direct Gemini extracted {len(reviews)} reviews")
            return reviews
            
        except Exception as e:
            print(f"Direct Gemini error: {e}")
            return []