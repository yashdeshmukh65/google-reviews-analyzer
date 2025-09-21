"""
Real-time Google Maps Review Scraper with updated selectors
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

class RealTimeScraper:
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
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    
    async def scrape_reviews(self, url, max_reviews=100):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
        
        self.log(f"🚀 Starting REAL-TIME scrape: {url}")
        
        driver = None
        try:
            driver = self.setup_chrome_driver()
            self.log("✅ Chrome driver ready")
            
            # Load page
            driver.get(url)
            time.sleep(5)
            
            # Get business name
            try:
                business_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
                )
                business_name = business_elem.text.strip()
                self.business_info = {
                    'name': business_name,
                    'url': url,
                    'scraped_at': datetime.now().isoformat()
                }
                self.log(f"🏢 Business: {business_name}")
            except:
                self.business_info = {'name': 'Unknown Business', 'url': url, 'scraped_at': datetime.now().isoformat()}
            
            # Find reviews section - try multiple approaches
            reviews_found = self.find_reviews_section(driver)
            
            if reviews_found:
                # Wait longer for reviews to load and try multiple selectors
                time.sleep(8)
                
                # Try multiple review element selectors
                review_selectors = [
                    '[data-review-id]',
                    '.jftiEf',
                    '.MyEned', 
                    '.fontBodyMedium',
                    '.wiI7pd',
                    '[jsaction*="review"]',
                    '.review-dialog-list > div',
                    '[role="listitem"]',
                    '.ODSEW-ShBeI'
                ]
                
                review_elements = []
                for selector in review_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        review_elements = elements
                        self.log(f"✅ Found {len(elements)} review elements with {selector}")
                        break
                
                if not review_elements:
                    self.log("❌ No review elements found with any selector")
                    return []
                
                # Load more reviews by scrolling
                self.load_more_reviews(driver, max_reviews)
                
                # Extract reviews
                reviews = self.extract_reviews(driver)
                
                if reviews:
                    # Limit to exact number requested
                    self.reviews_data = reviews[:max_reviews]
                    self.log(f"✅ Extracted {len(self.reviews_data)} real reviews (limit: {max_reviews})!")
                    return self.reviews_data
            
            self.log("❌ No reviews found")
            return []
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def find_reviews_section(self, driver):
        """Find and navigate to reviews section"""
        self.log("🔍 Finding Reviews tab (not Menu)...")
        
        # Wait for tabs to load
        time.sleep(3)
        
        # Method 1: Find all tab buttons and click the Reviews one
        try:
            # Look for tab container
            tab_containers = driver.find_elements(By.CSS_SELECTOR, '[role="tablist"], .RWPxGd')
            
            for container in tab_containers:
                buttons = container.find_elements(By.CSS_SELECTOR, 'button, [role="tab"]')
                self.log(f"Found {len(buttons)} tabs in container")
                
                for i, button in enumerate(buttons):
                    try:
                        # Get button text and aria-label
                        button_text = button.text.strip().lower()
                        aria_label = (button.get_attribute('aria-label') or '').lower()
                        
                        self.log(f"Tab {i+1}: text='{button_text}', aria-label='{aria_label}'")
                        
                        # Check if this is the Reviews tab (not Menu)
                        if ('review' in button_text or 'review' in aria_label) and 'menu' not in button_text and 'menu' not in aria_label:
                            if button.is_displayed() and button.is_enabled():
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(4)
                                self.log(f"✅ Clicked REVIEWS tab (not menu)")
                                return True
                    except Exception as e:
                        self.log(f"Error checking tab {i+1}: {e}")
                        continue
        except Exception as e:
            self.log(f"Error finding tab container: {e}")
        
        # Method 2: Try specific Reviews selectors
        reviews_selectors = [
            'button[data-value="Sort"]',
            'button[aria-label*="Reviews"]',
            '[data-tab-index="2"]',  # Reviews is usually 3rd tab (index 2)
            'button:contains("Reviews")',
        ]
        
        for selector in reviews_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        text = (elem.get_attribute('aria-label') or elem.text or '').lower()
                        if 'review' in text and 'menu' not in text:
                            driver.execute_script("arguments[0].click();", elem)
                            time.sleep(4)
                            self.log(f"✅ Clicked Reviews tab with selector: {selector}")
                            return True
            except:
                continue
        
        # Method 3: Click third tab (Reviews is typically 3rd: Overview, Menu, Reviews, About)
        try:
            all_tabs = driver.find_elements(By.CSS_SELECTOR, '[role="tablist"] button, .RWPxGd button')
            if len(all_tabs) >= 3:
                reviews_tab = all_tabs[2]  # Index 2 = 3rd tab = Reviews
                if reviews_tab.is_displayed() and reviews_tab.is_enabled():
                    driver.execute_script("arguments[0].click();", reviews_tab)
                    time.sleep(4)
                    self.log("✅ Clicked 3rd tab (should be Reviews)")
                    return True
        except Exception as e:
            self.log(f"Error clicking 3rd tab: {e}")
        
        return False
    
    def load_more_reviews(self, driver, max_reviews):
        """Load more reviews by scrolling the reviews container"""
        self.log(f"📜 Loading reviews with container scrolling...")
        
        # Find scrollable reviews container
        scrollable_container = None
        try:
            # Try to find the reviews scrollable area
            containers = driver.find_elements(By.CSS_SELECTOR, '.m6QErb, [role="main"], .siAUzd')
            for container in containers:
                if container.is_displayed():
                    scrollable_container = container
                    self.log("✅ Found scrollable reviews container")
                    break
        except:
            pass
        
        for scroll in range(30):
            # Scroll within container or window
            if scrollable_container:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_container)
            else:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(2)
            
            # Click "More" buttons
            more_selectors = ['button[aria-label*="more" i]', '.w8nwRe', 'button:contains("More")']
            for selector in more_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons[:2]:
                        if btn.is_displayed() and btn.is_enabled():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(1.5)
                            self.log("   ✅ Clicked more button")
                except:
                    continue
            
            # Count reviews
            review_count = len(driver.find_elements(By.CSS_SELECTOR, '[data-review-id], .jftiEf, .MyEned'))
            self.log(f"   Scroll {scroll+1}: {review_count} reviews loaded")
            
            if review_count >= max_reviews or review_count > 50:
                break
                
            if scroll > 5 and review_count < 3:
                self.log("⚠️ No reviews loading")
                break
                
            time.sleep(random.uniform(1, 2))
    
    def extract_reviews(self, driver):
        """Universal review extraction for any Google Maps business"""
        self.log("📋 Universal review extraction...")
        
        reviews = []
        
        # Comprehensive container selectors for universal compatibility
        container_selectors = [
            '[data-review-id]',
            '.jftiEf',
            '.MyEned',
            '.fontBodyMedium',
            '.wiI7pd',
            '[jsaction*="review"]',
            '.ODSEW-ShBeI',
            '[role="listitem"]',
            'div[data-review-id]',
            '.review-dialog-list > div',
            '.section-review',
            '.review-item',
            '.gws-localreviews__google-review',
            '[data-hveid] > div',
            '.Jtu6Td'
        ]
        
        containers = []
        for selector in container_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                # Filter elements that actually contain review content
                valid_containers = []
                for elem in elements:
                    try:
                        text = elem.text.lower()
                        if len(text) > 20 and any(word in text for word in ['star', 'ago', 'month', 'week', 'day']):
                            valid_containers.append(elem)
                    except:
                        continue
                
                if valid_containers:
                    containers = valid_containers
                    self.log(f"Found {len(containers)} valid review containers using {selector}")
                    break
        
        if not containers:
            self.log("❌ No valid review containers found")
            return []
        
        for i, container in enumerate(containers):
            # Stop if we've reached the limit
            if len(reviews) >= 100:  # Hard limit to prevent over-extraction
                self.log(f"✅ Reached extraction limit: {len(reviews)} reviews")
                break
                
            try:
                # Extract reviewer name
                name = self.extract_reviewer_name(container)
                if not name or name in ['Unknown', 'User']:
                    continue
                
                # Extract rating
                rating = self.extract_rating(container)
                if not rating:
                    continue
                
                # Extract review text
                text = self.extract_review_text(container)
                if not text or len(text) < 10:
                    continue
                
                # Extract date
                date = self.extract_date(container)
                
                review = {
                    'reviewer_name': name,
                    'shop_name': self.business_info.get('name', 'Unknown Business'),
                    'rating': rating,
                    'review_text': text,
                    'review_date': date
                }
                
                reviews.append(review)
                self.log(f"   ✅ Review {len(reviews)}: {name} - {rating}⭐")
                
            except Exception as e:
                self.log(f"   ❌ Error extracting review {i+1}: {e}")
                continue
        
        return reviews
    
    def extract_reviewer_name(self, container):
        """Universal reviewer name extraction"""
        name_selectors = [
            '.d4r55',
            '.X43Kjb', 
            '.TSUbDb',
            '.WNxzHc',
            '[data-value]',
            '.NuEeue',
            '.fontBodyMedium a',
            '.fontBodyMedium span',
            'a[data-value]',
            '.review-dialog-list .fontBodyMedium',
            '.section-review-title',
            '.review-author',
            '.author-name',
            'span[data-value]',
            '.gws-localreviews__google-review .fontBodyMedium',
            'a[href*="contrib"]'
        ]
        
        for selector in name_selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                name = elem.text.strip()
                # Universal name validation
                if (name and len(name) > 1 and not name.isdigit() and 
                    name.lower() not in ['google user', 'user', 'local guide', 'reviewer']):
                    return name
            except:
                continue
        return None
    
    def extract_rating(self, container):
        """Extract rating from container"""
        rating_selectors = [
            '[role="img"][aria-label*="star"]',
            '[aria-label*="star"]',
            '.kvMYJc'
        ]
        
        for selector in rating_selectors:
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
    
    def extract_review_text(self, container):
        """Universal review text extraction"""
        text_selectors = [
            '.wiI7pd',
            '.MyEned span',
            '.rsqaWe',
            '.ODSEW-ShBeI-text',
            '.Jtu6Td',
            '.fontBodyMedium span',
            '[data-expandable-section]',
            '.review-dialog-list .fontBodyMedium span',
            '.section-review-text',
            '.review-content',
            '.review-text',
            '.gws-localreviews__google-review .fontBodyMedium span',
            '.review-full-text',
            'span[jsaction*="expand"]'
        ]
        
        for selector in text_selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                text = elem.text.strip()
                # Universal text validation
                if (text and len(text) > 10 and not text.isdigit() and 
                    not text.lower().startswith('translate') and
                    'star' not in text.lower()):
                    return text
            except:
                continue
        return None
    
    def extract_date(self, container):
        """Extract date from container"""
        date_selectors = [
            '.rsqaWe', '.p34Ii', '.DU9Pgb',
            '.dehysf', '.WMbnJf'
        ]
        
        for selector in date_selectors:
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
real_time_scraper = RealTimeScraper()