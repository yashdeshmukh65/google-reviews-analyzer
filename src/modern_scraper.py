"""
Modern Google Maps Review Scraper with 2024 selectors
"""

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
import re

class ModernScraper:
    def __init__(self):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        self.debug_messages.append(log_msg)
        print(log_msg)
    
    def setup_chrome_driver(self):
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
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
        
        self.log(f"🚀 Modern scraper starting: {url}")
        
        driver = None
        try:
            driver = self.setup_chrome_driver()
            self.log("✅ Chrome ready")
            
            # Load page
            driver.get(url)
            time.sleep(10)  # Wait for full page load
            
            # Get business name
            business_name = self.get_business_name(driver)
            self.business_info = {
                'name': business_name,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            self.log(f"🏢 Business: {business_name}")
            
            # Navigate to reviews
            if self.navigate_to_reviews(driver):
                # Load reviews
                self.load_reviews(driver, max_reviews)
                
                # Extract reviews
                reviews = self.extract_reviews(driver, max_reviews)
                
                if reviews:
                    self.reviews_data = reviews
                    self.log(f"✅ Extracted {len(self.reviews_data)} reviews!")
                    return self.reviews_data
            
            self.log("❌ No reviews found")
            return []
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def get_business_name(self, driver):
        """Get business name with modern selectors"""
        selectors = [
            "h1.DUwDvf",
            "h1",
            "[data-attrid='title'] span",
            ".x3AX1-LfntMc-header-title-title",
            ".qrShPb h1"
        ]
        
        for selector in selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                name = element.text.strip()
                if name and len(name) > 1:
                    return name
            except:
                continue
        
        return "Unknown Business"
    
    def navigate_to_reviews(self, driver):
        """Navigate to reviews section with modern approach"""
        self.log("🔍 Looking for reviews...")
        
        # Wait for page to stabilize
        time.sleep(5)
        
        # Method 1: Look for reviews tab in tab list
        try:
            # Find all tabs
            tabs = driver.find_elements(By.CSS_SELECTOR, "button[role='tab'], .hh2c6, [data-tab-index]")
            self.log(f"Found {len(tabs)} tabs")
            
            for i, tab in enumerate(tabs):
                try:
                    tab_text = tab.get_attribute('aria-label') or tab.text or ''
                    self.log(f"Tab {i+1}: '{tab_text}'")
                    
                    if 'review' in tab_text.lower() and 'menu' not in tab_text.lower():
                        driver.execute_script("arguments[0].click();", tab)
                        time.sleep(5)
                        self.log("✅ Clicked reviews tab")
                        return True
                except Exception as e:
                    self.log(f"Error checking tab {i+1}: {e}")
                    continue
        except Exception as e:
            self.log(f"Error finding tabs: {e}")
        
        # Method 2: Try direct selectors
        review_selectors = [
            'button[data-value="Sort"]',
            'button[aria-label*="Reviews"]',
            'button[aria-label*="review"]'
        ]
        
        for selector in review_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        driver.execute_script("arguments[0].click();", elem)
                        time.sleep(5)
                        self.log(f"✅ Clicked reviews with {selector}")
                        return True
            except:
                continue
        
        # Method 3: Scroll to find reviews
        self.log("📜 Scrolling to find reviews...")
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
            
            if self.check_reviews_present(driver):
                self.log("✅ Found reviews by scrolling")
                return True
        
        return False
    
    def check_reviews_present(self, driver):
        """Check if reviews are present on page"""
        indicators = [
            '[data-review-id]',
            '.jftiEf',
            '.MyEned',
            '[aria-label*="stars"]',
            '.fontBodyMedium'
        ]
        
        for selector in indicators:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        return False
    
    def load_reviews(self, driver, max_reviews):
        """Load reviews by scrolling"""
        self.log(f"📜 Loading {max_reviews} reviews...")
        
        # Find scrollable area
        scrollable = None
        scroll_selectors = ['.m6QErb', '[role="main"]', '.siAUzd']
        
        for selector in scroll_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                if elem:
                    scrollable = elem
                    break
            except:
                continue
        
        # Scroll to load reviews
        for scroll in range(30):
            # Scroll
            if scrollable:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable)
            else:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(2)
            
            # Click "More" buttons
            more_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="more" i], .w8nwRe')
            for btn in more_buttons[:2]:
                try:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(1)
                except:
                    pass
            
            # Count reviews
            review_count = len(driver.find_elements(By.CSS_SELECTOR, '[data-review-id], .jftiEf, .MyEned'))
            self.log(f"   Scroll {scroll+1}: {review_count} reviews")
            
            if review_count >= max_reviews:
                self.log(f"✅ Reached target: {max_reviews} reviews")
                break
                
            if scroll > 5 and review_count < 3:
                break
                
            time.sleep(random.uniform(1, 2))
    
    def extract_reviews(self, driver, max_reviews):
        """Extract reviews with modern selectors"""
        self.log(f"📋 Extracting up to {max_reviews} reviews...")
        
        # Find review containers
        containers = []
        container_selectors = [
            '[data-review-id]',
            '.jftiEf',
            '.MyEned',
            '.fontBodyMedium'
        ]
        
        for selector in container_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                containers = elements
                self.log(f"Using {len(containers)} containers from {selector}")
                break
        
        if not containers:
            self.log("❌ No review containers found")
            return []
        
        reviews = []
        for i, container in enumerate(containers):
            if len(reviews) >= max_reviews:
                self.log(f"✅ Reached limit: {max_reviews} reviews extracted")
                break
                
            try:
                review = self.extract_single_review(container)
                if review:
                    reviews.append(review)
                    self.log(f"   ✅ Review {len(reviews)}: {review['reviewer_name']} - {review['rating']}⭐")
            except Exception as e:
                self.log(f"   ❌ Error extracting review {i+1}: {e}")
                continue
        
        return reviews
    
    def extract_single_review(self, container):
        """Extract single review data"""
        # Get reviewer name
        name = self.get_reviewer_name(container)
        if not name:
            return None
        
        # Get rating
        rating = self.get_rating(container)
        if not rating:
            return None
        
        # Get review text
        text = self.get_review_text(container)
        if not text:
            return None
        
        # Get date
        date = self.get_date(container)
        
        return {
            'reviewer_name': name,
            'shop_name': self.business_info.get('name', 'Unknown Business'),
            'rating': rating,
            'review_text': text,
            'review_date': date
        }
    
    def get_reviewer_name(self, container):
        """Extract reviewer name"""
        selectors = [
            '.d4r55',
            '.X43Kjb',
            '.TSUbDb',
            '.WNxzHc',
            '.fontBodyMedium a',
            'a[data-value]'
        ]
        
        for selector in selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                name = elem.text.strip()
                if name and len(name) > 1 and name.lower() not in ['google user', 'user']:
                    return name
            except:
                continue
        return None
    
    def get_rating(self, container):
        """Extract rating"""
        selectors = [
            '[role="img"][aria-label*="star"]',
            '[aria-label*="star"]',
            '.kvMYJc'
        ]
        
        for selector in selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                aria_label = elem.get_attribute('aria-label') or ''
                match = re.search(r'(\d+)', aria_label)
                if match:
                    rating = int(match.group(1))
                    if 1 <= rating <= 5:
                        return rating
            except:
                continue
        return None
    
    def get_review_text(self, container):
        """Extract review text"""
        selectors = [
            '.wiI7pd',
            '.MyEned span',
            '.rsqaWe',
            '.fontBodyMedium span'
        ]
        
        for selector in selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                text = elem.text.strip()
                if text and len(text) > 10:
                    return text
            except:
                continue
        return None
    
    def get_date(self, container):
        """Extract date"""
        selectors = [
            '.rsqaWe',
            '.p34Ii',
            '.DU9Pgb',
            '.dehysf'
        ]
        
        for selector in selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                date_text = elem.text.strip()
                if date_text and any(word in date_text.lower() for word in ['ago', 'month', 'week', 'day']):
                    return date_text
            except:
                continue
        return "Recent"
    
    def clear_data(self):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
    
    def get_debug_log(self):
        return "\n".join(self.debug_messages)

# Create global instance
modern_scraper = ModernScraper()