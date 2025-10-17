"""
Working Google Maps Review Scraper - Simplified and Effective
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

class WorkingScraper:
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
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    async def scrape_reviews(self, url, max_reviews=50):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
        
        self.log(f"🚀 Starting scrape: {url}")
        
        driver = None
        try:
            driver = self.setup_chrome_driver()
            self.log("✅ Chrome ready")
            
            # Load page
            driver.get(url)
            time.sleep(8)  # Wait longer for full load
            
            # Get business name
            business_name = self.get_business_name(driver)
            self.business_info = {
                'name': business_name,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            self.log(f"🏢 Business: {business_name}")
            
            # Find and click Reviews tab
            if self.click_reviews_tab(driver):
                time.sleep(5)
                
                # Scroll to load reviews
                self.scroll_to_load_reviews(driver, max_reviews)
                
                # Extract reviews
                reviews = self.extract_all_reviews(driver)
                
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
                driver.quit()
    
    def get_business_name(self, driver):
        """Get business name"""
        try:
            name_elem = driver.find_element(By.CSS_SELECTOR, "h1")
            return name_elem.text.strip()
        except:
            return "Unknown Business"
    
    def click_reviews_tab(self, driver):
        """Click the Reviews tab"""
        self.log("🔍 Looking for Reviews tab...")
        
        # Wait for tabs to appear
        time.sleep(3)
        
        # Try to find all clickable elements that might be the Reviews tab
        possible_selectors = [
            'button[role="tab"]',
            '[role="tablist"] button',
            '.hh2c6',
            'button[data-value="Sort"]',
            'button[aria-label*="review" i]'
        ]
        
        for selector in possible_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                self.log(f"Found {len(elements)} elements with {selector}")
                
                for i, elem in enumerate(elements):
                    try:
                        # Get text content
                        text = elem.text.lower()
                        aria_label = (elem.get_attribute('aria-label') or '').lower()
                        
                        self.log(f"  Element {i+1}: text='{text}', aria='{aria_label}'")
                        
                        # Check if this looks like Reviews tab
                        if ('review' in text or 'review' in aria_label) and 'menu' not in text:
                            if elem.is_displayed() and elem.is_enabled():
                                driver.execute_script("arguments[0].click();", elem)
                                self.log(f"✅ Clicked Reviews tab!")
                                return True
                    except Exception as e:
                        continue
            except:
                continue
        
        # Fallback: try clicking 3rd tab (usually Reviews)
        try:
            all_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[role="tab"], .hh2c6')
            if len(all_buttons) >= 3:
                third_button = all_buttons[2]
                if third_button.is_displayed():
                    driver.execute_script("arguments[0].click();", third_button)
                    self.log("✅ Clicked 3rd tab (Reviews)")
                    return True
        except:
            pass
        
        return False
    
    def scroll_to_load_reviews(self, driver, max_reviews):
        """Aggressively scroll to load exact number of reviews"""
        self.log(f"📜 Loading {max_reviews} reviews...")
        
        # Calculate scroll attempts based on target reviews
        max_scrolls = min(60, max(25, max_reviews // 8))
        
        for scroll in range(max_scrolls):
            # Multiple scroll actions per iteration
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
            
            # Click "More" buttons aggressively
            more_selectors = [
                'button[aria-label*="more" i]',
                '.w8nwRe',
                'button[jsaction*="review"]',
                '[data-value="Sort"] ~ button',
                'button:contains("More")',
                '.gws-localreviews__google-reviews button'
            ]
            
            for selector in more_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons[:3]:  # Try more buttons
                        if btn.is_displayed() and btn.is_enabled():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(0.3)
                except:
                    continue
            
            # Count current reviews with multiple selectors
            review_selectors = ['[data-review-id]', '.jftiEf', '.MyEned']
            review_count = 0
            for selector in review_selectors:
                count = len(driver.find_elements(By.CSS_SELECTOR, selector))
                review_count = max(review_count, count)
            
            self.log(f"  Scroll {scroll+1}/{max_scrolls}: {review_count} reviews (target: {max_reviews})")
            
            # Stop if we have enough reviews
            if review_count >= max_reviews:
                self.log(f"✅ Reached target: {review_count} reviews")
                break
            
            # Stop if no progress for several scrolls
            if scroll > 15 and review_count < 10:
                self.log("⚠️ No reviews loading, stopping")
                break
            
            # Dynamic wait based on progress
            if scroll % 10 == 0:
                time.sleep(3)  # Longer wait every 10 scrolls
            else:
                time.sleep(1)
    
    def extract_all_reviews(self, driver):
        """Extract all reviews from page"""
        self.log("📋 Extracting reviews...")
        
        reviews = []
        
        # Find review containers
        containers = driver.find_elements(By.CSS_SELECTOR, '[data-review-id]')
        
        if not containers:
            # Try alternative selectors
            alt_selectors = ['.jftiEf', '.MyEned', '.fontBodyMedium']
            for selector in alt_selectors:
                containers = driver.find_elements(By.CSS_SELECTOR, selector)
                if containers:
                    self.log(f"Using {len(containers)} containers from {selector}")
                    break
        
        if not containers:
            self.log("❌ No review containers found")
            return []
        
        self.log(f"Found {len(containers)} review containers")
        
        # Process all containers to get maximum reviews
        for i, container in enumerate(containers):
            # Stop if we have enough reviews
            if len(reviews) >= 500:  # Hard limit to prevent memory issues
                break
                
            try:
                review = self.extract_single_review(container, driver)
                if review:
                    reviews.append(review)
                    self.log(f"  ✅ Review {len(reviews)}: {review['reviewer_name']} - {review['rating']}⭐")
            except Exception as e:
                self.log(f"  ❌ Error extracting review {i+1}: {e}")
                continue
        
        return reviews
    
    def extract_single_review(self, container, driver):
        """Extract single review data"""
        try:
            # Get reviewer name - try multiple approaches
            name = None
            name_selectors = [
                '.d4r55', '.X43Kjb', '.TSUbDb', '.WNxzHc', 
                'a[data-value]', '.fontBodyMedium a', 'span[data-value]'
            ]
            
            for selector in name_selectors:
                try:
                    elem = container.find_element(By.CSS_SELECTOR, selector)
                    name = elem.text.strip()
                    if name and len(name) > 1 and name.lower() not in ['google user', 'user']:
                        break
                except:
                    continue
            
            if not name:
                return None
            
            # Get rating
            rating = None
            try:
                rating_elem = container.find_element(By.CSS_SELECTOR, '[role="img"][aria-label*="star"]')
                aria_label = rating_elem.get_attribute('aria-label')
                match = re.search(r'(\d+)', aria_label)
                if match:
                    rating = int(match.group(1))
            except:
                pass
            
            if not rating:
                return None
            
            # Get review text
            text = None
            text_selectors = ['.wiI7pd', '.MyEned span', '.rsqaWe', '.fontBodyMedium span']
            
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
            
            # Get date
            date = "Recent"
            try:
                date_elem = container.find_element(By.CSS_SELECTOR, '.rsqaWe, .p34Ii')
                date = date_elem.text.strip()
            except:
                pass
            
            return {
                'reviewer_name': name,
                'shop_name': self.business_info.get('name', 'Unknown Business'),
                'rating': rating,
                'review_text': text,
                'review_date': date
            }
            
        except Exception as e:
            return None
    
    def clear_data(self):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
    
    def get_debug_log(self):
        return "\n".join(self.debug_messages)

# Create global instance
working_scraper = WorkingScraper()