"""
Render-optimized Google Maps Review Scraper
"""

import time
import random
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

class RenderScraper:
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
        """Setup Chrome for Render deployment"""
        chrome_options = Options()
        
        # Render-specific Chrome options
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Try different Chrome binary paths for Render
        chrome_paths = [
            "/usr/bin/google-chrome-stable",
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium"
        ]
        
        for path in chrome_paths:
            if os.path.exists(path):
                chrome_options.binary_location = path
                self.log(f"Using Chrome binary: {path}")
                break
        
        try:
            # Try to use system ChromeDriver first
            service = Service()
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            try:
                # Fallback to webdriver-manager
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                self.log(f"ChromeDriver setup failed: {e}")
                return None
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    
    async def scrape_reviews(self, url, max_reviews=100):
        """Optimized scraping for Render with timeout handling"""
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
        
        self.log(f"🚀 Render scrape: {url}")
        
        driver = None
        try:
            driver = self.setup_chrome_driver()
            if not driver:
                self.log("❌ Chrome setup failed")
                return []
            
            self.log("✅ Chrome ready")
            
            # Set page load timeout for Render
            driver.set_page_load_timeout(30)
            driver.implicitly_wait(10)
            
            # Load page
            driver.get(url)
            time.sleep(3)  # Reduced wait time
            
            # Get business name
            business_name = self.get_business_name(driver)
            self.business_info = {
                'name': business_name,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            self.log(f"🏢 Business: {business_name}")
            
            # Find Reviews tab with timeout
            if self.click_reviews_tab(driver):
                time.sleep(2)  # Reduced wait
                
                # Optimized review loading
                self.load_reviews_optimized(driver, max_reviews)
                
                # Extract reviews
                reviews = self.extract_reviews_fast(driver)
                
                if reviews:
                    self.reviews_data = reviews[:max_reviews]
                    self.log(f"✅ Extracted {len(self.reviews_data)} reviews!")
                    return self.reviews_data
            
            self.log("❌ No reviews extracted")
            return []
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return []
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
    
    def get_business_name(self, driver):
        """Quick business name extraction"""
        try:
            name_elem = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
            )
            return name_elem.text.strip()
        except:
            return "Unknown Business"
    
    def click_reviews_tab(self, driver):
        """Fast Reviews tab detection"""
        self.log("🔍 Finding Reviews tab...")
        
        selectors = [
            'button[role="tab"][aria-label*="review" i]',
            'button[data-value="Sort"]',
            '.hh2c6'
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    text = (elem.text + elem.get_attribute('aria-label')).lower()
                    if 'review' in text and 'menu' not in text:
                        if elem.is_displayed():
                            driver.execute_script("arguments[0].click();", elem)
                            self.log("✅ Clicked Reviews tab")
                            return True
            except:
                continue
        
        return False
    
    def load_reviews_optimized(self, driver, max_reviews):
        """Optimized review loading for Render"""
        self.log(f"📜 Loading {max_reviews} reviews...")
        
        max_scrolls = min(40, max(15, max_reviews // 10))
        
        for scroll in range(max_scrolls):
            # Multiple scrolls per iteration
            for _ in range(2):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
            
            # Try to click more buttons
            try:
                more_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="more" i], .w8nwRe')
                for btn in more_buttons[:2]:
                    if btn.is_displayed() and btn.is_enabled():
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(0.5)
            except:
                pass
            
            # Count reviews
            review_count = len(driver.find_elements(By.CSS_SELECTOR, '[data-review-id]'))
            self.log(f"  Scroll {scroll+1}/{max_scrolls}: {review_count} reviews (target: {max_reviews})")
            
            if review_count >= max_reviews:
                self.log(f"✅ Reached target: {review_count} reviews")
                break
            
            if scroll > 10 and review_count < 5:
                break
    
    def extract_reviews_fast(self, driver):
        """Fast review extraction"""
        self.log("📋 Extracting reviews...")
        
        reviews = []
        containers = driver.find_elements(By.CSS_SELECTOR, '[data-review-id]')
        
        if not containers:
            containers = driver.find_elements(By.CSS_SELECTOR, '.jftiEf, .MyEned')
        
        self.log(f"Found {len(containers)} containers")
        
        for container in containers:  # Process all containers
            try:
                review = self.extract_single_review_fast(container)
                if review:
                    reviews.append(review)
            except:
                continue
        
        return reviews
    
    def extract_single_review_fast(self, container):
        """Fast single review extraction"""
        try:
            # Name
            name_selectors = ['.d4r55', '.X43Kjb', 'a[data-value]']
            name = None
            for selector in name_selectors:
                try:
                    elem = container.find_element(By.CSS_SELECTOR, selector)
                    name = elem.text.strip()
                    if name and len(name) > 1:
                        break
                except:
                    continue
            
            if not name:
                return None
            
            # Rating
            try:
                rating_elem = container.find_element(By.CSS_SELECTOR, '[role="img"][aria-label*="star"]')
                aria_label = rating_elem.get_attribute('aria-label')
                match = re.search(r'(\d+)', aria_label)
                rating = int(match.group(1)) if match else None
            except:
                rating = None
            
            if not rating:
                return None
            
            # Text
            text_selectors = ['.wiI7pd', '.MyEned span', '.rsqaWe']
            text = None
            for selector in text_selectors:
                try:
                    elem = container.find_element(By.CSS_SELECTOR, selector)
                    text = elem.text.strip()
                    if text and len(text) > 10:
                        break
                except:
                    continue
            
            if not text:
                return None
            
            # Date
            try:
                date_elem = container.find_element(By.CSS_SELECTOR, '.rsqaWe, .p34Ii')
                date = date_elem.text.strip()
            except:
                date = "Recent"
            
            return {
                'reviewer_name': name,
                'shop_name': self.business_info.get('name', 'Unknown Business'),
                'rating': rating,
                'review_text': text,
                'review_date': date
            }
            
        except:
            return None
    
    def clear_data(self):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
    
    def get_debug_log(self):
        return "\n".join(self.debug_messages)

# Global instance
render_scraper = RenderScraper()