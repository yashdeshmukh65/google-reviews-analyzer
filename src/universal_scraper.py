"""
Universal Google Maps Review Scraper
Works with any Google Maps business URL
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

class UniversalScraper:
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
        
        self.log(f"🚀 Universal scraper starting for: {url}")
        
        driver = None
        try:
            driver = self.setup_chrome_driver()
            self.log("✅ Chrome driver ready")
            
            # Load page
            driver.get(url)
            time.sleep(8)  # Longer wait for page load
            
            # Get business name with multiple approaches
            business_name = self.extract_business_name(driver)
            self.business_info = {
                'name': business_name,
                'url': url,
                'scraped_at': datetime.now().isoformat()
            }
            self.log(f"🏢 Business: {business_name}")
            
            # Universal approach to find reviews
            reviews = self.universal_review_extraction(driver, max_reviews)
            
            if reviews:
                self.reviews_data = reviews[:max_reviews]
                self.log(f"✅ Extracted {len(self.reviews_data)} reviews!")
                return self.reviews_data
            else:
                self.log("❌ No reviews found")
                return []
            
        except Exception as e:
            self.log(f"❌ Error: {e}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def extract_business_name(self, driver):
        """Extract business name using multiple selectors"""
        name_selectors = [
            "h1",
            "[data-attrid='title'] span",
            ".x3AX1-LfntMc-header-title-title",
            ".SPZz6b h1",
            ".qrShPb h1",
            ".x3AX1-LfntMc-header-title"
        ]
        
        for selector in name_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                name = element.text.strip()
                if name and len(name) > 1:
                    return name
            except:
                continue
        
        return "Unknown Business"
    
    def universal_review_extraction(self, driver, max_reviews):
        """Universal method to extract reviews from any Google Maps page"""
        self.log("🔍 Starting universal review extraction...")
        
        # Step 1: Try to find and click reviews tab/section
        self.navigate_to_reviews(driver)
        
        # Step 2: Load more reviews by scrolling
        self.load_more_reviews(driver, max_reviews)
        
        # Step 3: Extract all visible reviews
        return self.extract_all_reviews(driver)
    
    def navigate_to_reviews(self, driver):
        """Navigate to reviews section using multiple approaches"""
        self.log("🔍 Looking for reviews section...")
        
        # Approach 1: Click reviews tab
        tab_clicked = False
        tab_selectors = [
            'button[data-value="Sort"]',
            'button[aria-label*="Reviews"]',
            'button[aria-label*="review"]',
            '[data-tab-index="2"]',
            'div[role="tablist"] button:nth-child(3)',
            '.hh2c6'
        ]
        
        for selector in tab_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem.is_enabled():
                        text = (elem.get_attribute('aria-label') or elem.text or '').lower()
                        if 'review' in text and 'menu' not in text:
                            driver.execute_script("arguments[0].click();", elem)
                            time.sleep(5)
                            self.log(f"✅ Clicked reviews tab")
                            tab_clicked = True
                            break
            except:
                continue
            if tab_clicked:
                break
        
        # Approach 2: Scroll to find reviews if no tab found
        if not tab_clicked:
            self.log("📜 Scrolling to find reviews...")
            for _ in range(5):
                driver.execute_script("window.scrollBy(0, 500);")
                time.sleep(2)
                
                # Check if reviews are now visible
                if self.check_reviews_visible(driver):
                    self.log("✅ Found reviews by scrolling")
                    break
    
    def check_reviews_visible(self, driver):
        """Check if reviews are visible on page"""
        review_indicators = [
            '[data-review-id]',
            '.jftiEf',
            '.MyEned',
            '[aria-label*="star"]',
            '.fontBodyMedium'
        ]
        
        for selector in review_indicators:
            if driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        return False
    
    def load_more_reviews(self, driver, max_reviews):
        """Load more reviews by scrolling and clicking buttons"""
        self.log(f"📜 Loading up to {max_reviews} reviews...")
        
        # Find scrollable container
        scrollable_container = None
        container_selectors = ['.m6QErb', '[role="main"]', '.siAUzd', 'body']
        
        for selector in container_selectors:
            try:
                container = driver.find_element(By.CSS_SELECTOR, selector)
                if container:
                    scrollable_container = container
                    break
            except:
                continue
        
        # Scroll and load reviews
        for scroll in range(40):  # More scrolls for universal compatibility
            # Scroll within container
            if scrollable_container and scrollable_container.tag_name != 'body':
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_container)
            else:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            time.sleep(2)
            
            # Try to click "More" buttons
            more_selectors = [
                'button[aria-label*="more" i]',
                'button[aria-label*="More" i]',
                '.w8nwRe',
                'button:contains("More")',
                '[jsaction*="more"]',
                'button[data-value="1"]'
            ]
            
            for selector in more_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons[:3]:
                        if btn.is_displayed() and btn.is_enabled():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(2)
                            self.log("   ✅ Clicked more button")
                except:
                    continue
            
            # Count current reviews
            review_count = self.count_reviews(driver)
            self.log(f"   Scroll {scroll+1}: {review_count} reviews found")
            
            if review_count >= max_reviews:
                break
                
            if scroll > 10 and review_count < 3:
                self.log("⚠️ No new reviews loading")
                break
                
            time.sleep(random.uniform(1, 2))
    
    def count_reviews(self, driver):
        """Count visible reviews using multiple selectors"""
        selectors = [
            '[data-review-id]',
            '.jftiEf',
            '.MyEned',
            '.fontBodyMedium',
            '.wiI7pd'
        ]
        
        max_count = 0
        for selector in selectors:
            count = len(driver.find_elements(By.CSS_SELECTOR, selector))
            max_count = max(max_count, count)
        
        return max_count
    
    def extract_all_reviews(self, driver):
        """Extract all visible reviews using comprehensive selectors"""
        self.log("📋 Extracting all reviews...")
        
        # Find all review containers
        container_selectors = [
            '[data-review-id]',
            '.jftiEf',
            '.MyEned',
            '.fontBodyMedium',
            '.wiI7pd',
            '[jsaction*="review"]'
        ]
        
        containers = []
        for selector in container_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                containers = elements
                self.log(f"Found {len(containers)} containers with {selector}")
                break
        
        if not containers:
            self.log("❌ No review containers found")
            return []
        
        reviews = []
        for i, container in enumerate(containers):
            try:
                review = self.extract_single_review(container)
                if review and self.is_valid_review(review):
                    reviews.append(review)
                    self.log(f"   ✅ Review {len(reviews)}: {review['reviewer_name']} - {review['rating']}⭐")
            except Exception as e:
                self.log(f"   ❌ Error extracting review {i+1}: {e}")
                continue
        
        return reviews
    
    def extract_single_review(self, container):
        """Extract data from a single review container"""
        # Extract reviewer name
        name = self.extract_reviewer_name(container)
        if not name:
            return None
        
        # Extract rating
        rating = self.extract_rating(container)
        if not rating:
            return None
        
        # Extract review text
        text = self.extract_review_text(container)
        if not text:
            return None
        
        # Extract date
        date = self.extract_date(container)
        
        return {
            'reviewer_name': name,
            'shop_name': self.business_info.get('name', 'Unknown Business'),
            'rating': rating,
            'review_text': text,
            'review_date': date
        }
    
    def extract_reviewer_name(self, container):
        """Extract reviewer name with comprehensive selectors"""
        name_selectors = [
            '.d4r55',
            '.X43Kjb',
            '.TSUbDb',
            '.WNxzHc',
            '.NuEeue',
            '.fontBodyMedium a',
            '.fontBodyMedium span',
            'a[data-value]',
            '[data-href*="contrib"]'
        ]
        
        for selector in name_selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                name = elem.text.strip()
                if name and len(name) > 1 and not name.isdigit() and name.lower() not in ['google user', 'user', 'local guide']:
                    return name
            except:
                continue
        return None
    
    def extract_rating(self, container):
        """Extract rating with comprehensive selectors"""
        rating_selectors = [
            '[role="img"][aria-label*="star"]',
            '[aria-label*="star"]',
            '.kvMYJc',
            '[data-value]',
            '.Fam1ne .fzvQIb'
        ]
        
        for selector in rating_selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                aria_label = elem.get_attribute('aria-label') or elem.get_attribute('data-value') or ''
                match = re.search(r'(\d+)', aria_label)
                if match:
                    rating = int(match.group(1))
                    if 1 <= rating <= 5:
                        return rating
            except:
                continue
        return None
    
    def extract_review_text(self, container):
        """Extract review text with comprehensive selectors"""
        text_selectors = [
            '.wiI7pd',
            '.MyEned span',
            '.rsqaWe',
            '.ODSEW-ShBeI-text',
            '.Jtu6Td',
            '.fontBodyMedium span',
            '[data-expandable-section]',
            '.review-text'
        ]
        
        for selector in text_selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                text = elem.text.strip()
                if text and len(text) > 10 and not text.isdigit():
                    return text
            except:
                continue
        return None
    
    def extract_date(self, container):
        """Extract date with comprehensive selectors"""
        date_selectors = [
            '.rsqaWe',
            '.p34Ii',
            '.DU9Pgb',
            '.dehysf',
            '.WMbnJf',
            '.RHo1pe',
            '.fontCaption'
        ]
        
        for selector in date_selectors:
            try:
                elem = container.find_element(By.CSS_SELECTOR, selector)
                date_text = elem.text.strip()
                if date_text and any(word in date_text.lower() for word in ['ago', 'month', 'week', 'day', 'year']):
                    return date_text
            except:
                continue
        return "Recent"
    
    def is_valid_review(self, review):
        """Validate if review has meaningful content"""
        if not review:
            return False
        
        # Check if reviewer name is meaningful
        if not review['reviewer_name'] or review['reviewer_name'] in ['Unknown', 'User', 'Google User']:
            return False
        
        # Check if review text is meaningful
        if not review['review_text'] or len(review['review_text']) < 10:
            return False
        
        # Check if rating is valid
        if not review['rating'] or not (1 <= review['rating'] <= 5):
            return False
        
        return True
    
    def clear_data(self):
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
    
    def get_debug_log(self):
        return "\n".join(self.debug_messages)

# Create global instance
universal_scraper = UniversalScraper()