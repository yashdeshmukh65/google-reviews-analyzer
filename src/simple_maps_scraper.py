"""
Simple Google Maps Review Scraper using only Selenium
Direct extraction without Crawl4AI for better reliability
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

class SimpleMapscraper:
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
        """Main scraping method using Selenium only with real-time detection"""
        # Clear any existing data first
        self.reviews_data = []
        self.business_info = {}
        self.debug_messages = []
        
        self.log(f"🚀 Starting REAL-TIME scrape for: {url}")
        self.log(f"📊 Target: {max_reviews} reviews")
        
        driver = None
        try:
            # Setup driver with better options
            driver = self.setup_chrome_driver()
            self.log("🌐 Chrome driver initialized")
            
            # Load page and wait
            driver.get(url)
            time.sleep(5)  # Longer initial wait
            
            # Extract business name
            try:
                business_name_elem = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h1, [data-attrid='title'] span"))
                )
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
            
            # Look for reviews section with enhanced detection
            self.log("🔍 Looking for reviews section...")
            
            # Try multiple approaches to find reviews
            reviews_found = False
            
            # Approach 1: Click reviews tab
            reviews_tab_selectors = [
                'button[data-value="Sort"]',
                'button[aria-label*="Reviews" i]',
                'button[aria-label*="review" i]',
                '[data-tab-index="1"]',
                '.hh2c6',
                'div[role="tablist"] button:nth-child(2)'
            ]
            
            for selector in reviews_tab_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            text = element.get_attribute('aria-label') or element.text or ''
                            if any(word in text.lower() for word in ['review', 'sort']):
                                driver.execute_script("arguments[0].click();", element)
                                time.sleep(4)
                                self.log(f"✅ Clicked reviews tab: {text}")
                                reviews_found = True
                                break
                except:
                    continue
                if reviews_found:
                    break
            
            # Approach 2: Scroll to reviews section
            if not reviews_found:
                self.log("🔍 Scrolling to find reviews section...")
                for _ in range(5):
                    driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)
                    # Check if reviews are now visible
                    review_indicators = driver.find_elements(By.CSS_SELECTOR, '[data-review-id], .jftiEf, [aria-label*="star"]')
                    if review_indicators:
                        self.log(f"✅ Found reviews after scrolling")
                        reviews_found = True
                        break
            
            # Approach 3: Direct URL manipulation (if it's a place URL)
            if not reviews_found and 'place/' in url:
                try:
                    # Try to navigate directly to reviews
                    reviews_url = url.replace('place/', 'place/') + '/reviews'
                    if reviews_url != url:
                        driver.get(reviews_url)
                        time.sleep(4)
                        self.log("🔄 Tried direct reviews URL")
                except:
                    pass
            
            # Enhanced scrolling with better review detection
            self.log(f"📜 Loading reviews with smart scrolling...")
            
            # First, try to click "Show more reviews" or similar buttons
            show_more_clicked = False
            show_more_selectors = [
                'button[aria-label*="more" i]',
                'button[aria-label*="Show" i]',
                '.w8nwRe',
                'button[jsaction*="review"]',
                '[data-value="Sort"] ~ button'
            ]
            
            for selector in show_more_selectors:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            btn_text = btn.get_attribute('aria-label') or btn.text or ''
                            if any(word in btn_text.lower() for word in ['more', 'show', 'load']):
                                driver.execute_script("arguments[0].click();", btn)
                                time.sleep(3)
                                self.log(f"   ✅ Clicked show more button: {btn_text}")
                                show_more_clicked = True
                                break
                except:
                    continue
                if show_more_clicked:
                    break
            
            # Aggressive scrolling to load all reviews
            for scroll in range(30):
                # Scroll down
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1.5, 2.5))
                
                # Try to expand "More" text in reviews
                try:
                    more_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label*="more" i], .w8nwRe')
                    for btn in more_buttons[:5]:
                        if btn.is_displayed() and btn.is_enabled():
                            driver.execute_script("arguments[0].click();", btn)
                            time.sleep(0.5)
                except:
                    pass
                
                # Count actual review containers
                review_elements = driver.find_elements(By.CSS_SELECTOR, '[data-review-id], .jftiEf, .MyEned')
                
                # Also check for reviews in different sections
                all_reviews = driver.find_elements(By.CSS_SELECTOR, '[jsaction*="review"], .gws-localreviews__google-review')
                total_found = max(len(review_elements), len(all_reviews))
                
                self.log(f"   Scroll {scroll+1}: Found {total_found} potential review elements")
                
                # Stop if we have enough or no new reviews are loading
                if total_found >= max_reviews or (scroll > 10 and total_found < 5):
                    self.log(f"✅ Stopping scroll - found {total_found} elements")
                    break
                    
                # Random delay to avoid detection
                time.sleep(random.uniform(0.5, 1.0))
            
            # Extract reviews
            self.log("📋 Extracting REAL review content...")
            reviews = self.extract_reviews_direct(driver)
            
            # Filter for real reviews only
            real_reviews = []
            for review in reviews:
                if (review['reviewer_name'] not in ['Unknown', 'User', ''] and 
                    len(review['review_text']) > 15 and 
                    review['rating'] is not None):
                    real_reviews.append(review)
            
            if real_reviews:
                self.reviews_data = real_reviews[:max_reviews]  # Limit to requested amount
                self.log(f"✅ Successfully extracted {len(self.reviews_data)} REAL reviews!")
                return self.reviews_data
            else:
                self.log("❌ No real reviews extracted")
                return []
            
        except Exception as e:
            self.log(f"❌ Scraping error: {e}")
            return []
        finally:
            if driver:
                driver.quit()
                self.log("🔒 Chrome driver closed")
    
    def extract_reviews_direct(self, driver):
        """Extract reviews using direct Selenium selectors with improved real-time detection"""
        reviews = []
        
        # Wait for reviews to load
        time.sleep(3)
        
        # More comprehensive review container selectors
        review_selectors = [
            '[data-review-id]',
            '.jftiEf',
            '.MyEned',
            '.fontBodyMedium',
            '.wiI7pd',
            '[jsaction*="review"]',
            '.gws-localreviews__google-review',
            '[role="listitem"]',
            '.ODSEW-ShBeI'
        ]
        
        review_containers = []
        for selector in review_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                # Filter out elements that don't look like review containers
                valid_elements = []
                for elem in elements:
                    try:
                        # Check if element contains review-like content
                        elem_text = elem.text.strip()
                        if len(elem_text) > 20 and ('star' in elem.get_attribute('innerHTML').lower() or 
                                                   'rating' in elem.get_attribute('innerHTML').lower() or
                                                   elem.find_elements(By.CSS_SELECTOR, '[role="img"]')):
                            valid_elements.append(elem)
                    except:
                        continue
                
                if valid_elements:
                    review_containers.extend(valid_elements)
                    self.log(f"   Found {len(valid_elements)} valid containers with {selector}")
        
        # Remove duplicates by checking element location
        unique_containers = []
        seen_locations = set()
        for container in review_containers:
            try:
                location = (container.location['x'], container.location['y'])
                if location not in seen_locations and location != (0, 0):
                    unique_containers.append(container)
                    seen_locations.add(location)
            except:
                continue
        
        review_containers = unique_containers
        self.log(f"📋 Processing {len(review_containers)} unique review containers")
        
        extracted_count = 0
        
        for i, container in enumerate(review_containers):
            if extracted_count >= 100:  # Hard limit
                break
                
            try:
                # Extract reviewer name with more selectors
                reviewer_name = None
                name_selectors = [
                    '.d4r55', '.X43Kjb', '.TSUbDb', '.WNxzHc', 
                    '[data-value]', '.NuEeue', '.TSUbDb a',
                    '.gws-localreviews__google-review .TSUbDb'
                ]
                
                for selector in name_selectors:
                    try:
                        name_elem = container.find_element(By.CSS_SELECTOR, selector)
                        name_text = name_elem.text.strip()
                        if name_text and len(name_text) > 1 and not name_text.isdigit():
                            reviewer_name = name_text
                            break
                    except:
                        continue
                
                # Skip if no real name found
                if not reviewer_name or reviewer_name in ['Unknown', 'User', '']:
                    continue
                
                # Extract rating with better detection
                rating = None
                rating_selectors = [
                    '[role="img"][aria-label*="star"]',
                    '[aria-label*="star"]',
                    '.kvMYJc',
                    '[data-value]'
                ]
                
                for selector in rating_selectors:
                    try:
                        rating_elem = container.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_elem.get_attribute('aria-label') or rating_elem.get_attribute('data-value') or rating_elem.text
                        if rating_text:
                            rating_match = re.search(r'(\d+)', rating_text)
                            if rating_match:
                                rating = int(rating_match.group(1))
                                if 1 <= rating <= 5:
                                    break
                    except:
                        continue
                
                # Skip if no valid rating
                if rating is None:
                    continue
                
                # Extract review text with comprehensive selectors
                review_text = None
                text_selectors = [
                    '.wiI7pd', '.MyEned span', '.rsqaWe', 
                    '.ODSEW-ShBeI-text', '.Jtu6Td', '.MyEned',
                    '[data-expandable-section]', '.gws-localreviews__google-review .Jtu6Td'
                ]
                
                for selector in text_selectors:
                    try:
                        text_elem = container.find_element(By.CSS_SELECTOR, selector)
                        text_content = text_elem.text.strip()
                        if text_content and len(text_content) > 10 and not text_content.isdigit():
                            review_text = text_content
                            break
                    except:
                        continue
                
                # Skip if no meaningful review text
                if not review_text or len(review_text) < 10:
                    continue
                
                # Extract date with better selectors
                review_date = "Recent"
                date_selectors = [
                    '.rsqaWe', '.p34Ii', '.DU9Pgb', '.dehysf', 
                    '.WMbnJf', '.RHo1pe', '.dehysf.lTi8oc'
                ]
                
                for selector in date_selectors:
                    try:
                        date_elem = container.find_element(By.CSS_SELECTOR, selector)
                        date_text = date_elem.text.strip()
                        if date_text and any(word in date_text.lower() for word in ['ago', 'month', 'week', 'day', 'year']):
                            review_date = date_text
                            break
                    except:
                        continue
                
                # Create review data with shop name
                review_data = {
                    'reviewer_name': reviewer_name,
                    'shop_name': self.business_info.get('name', 'Unknown Business'),
                    'rating': rating,
                    'review_text': review_text,
                    'review_date': review_date
                }
                
                reviews.append(review_data)
                extracted_count += 1
                self.log(f"   ✅ Review {extracted_count}: {reviewer_name} - {rating}⭐ - {review_date}")
                
            except Exception as e:
                self.log(f"   ❌ Error extracting review {i+1}: {e}")
                continue
        
        self.log(f"🎯 Successfully extracted {len(reviews)} real reviews")
        return reviews
    
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
simple_maps_scraper = SimpleMapscraper()