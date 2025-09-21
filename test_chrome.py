from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_chrome_setup():
    """Test if Chrome and Selenium are working"""
    try:
        print("Testing Chrome setup...")
        
        options = Options()
        # Don't use headless for testing
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        print("Chrome driver created successfully")
        
        # Test with Google
        driver.get("https://www.google.com")
        time.sleep(3)
        
        title = driver.title
        print(f"Page title: {title}")
        
        if "Google" in title:
            print("✅ Chrome setup is working!")
        else:
            print("❌ Chrome setup issue")
        
        driver.quit()
        return True
        
    except Exception as e:
        print(f"❌ Chrome setup failed: {e}")
        return False

if __name__ == "__main__":
    test_chrome_setup()