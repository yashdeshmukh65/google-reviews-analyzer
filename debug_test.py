import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_everything():
    print("=== DEBUGGING SCRAPER ISSUES ===\n")
    
    # Test 1: Check Gemini API
    print("1. Testing Gemini API...")
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            print(f"✅ API Key found: {api_key[:10]}...")
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content("Say 'Hello'")
            if response and response.text:
                print("✅ Gemini API working")
            else:
                print("❌ Gemini API not responding")
        else:
            print("❌ No Gemini API key found")
    except Exception as e:
        print(f"❌ Gemini error: {e}")
    
    print()
    
    # Test 2: Check Chrome installation
    print("2. Testing Chrome installation...")
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        print("   Installing ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        print("   Creating Chrome instance...")
        driver = webdriver.Chrome(service=service, options=options)
        print("   Testing navigation...")
        driver.get("https://www.google.com")
        title = driver.title
        print(f"   Page title: {title}")
        driver.quit()
        
        if "Google" in title:
            print("✅ Chrome and Selenium working")
        else:
            print("❌ Chrome navigation issue")
            
    except Exception as e:
        print(f"❌ Chrome/Selenium error: {e}")
    
    print()
    
    # Test 3: Test with actual Google Maps URL
    print("3. Testing Google Maps access...")
    try:
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        # Remove headless to see what happens
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        test_url = "https://www.google.com/maps/place/Domino's+Pizza"
        print(f"   Loading: {test_url}")
        driver.get(test_url)
        
        import time
        time.sleep(5)
        
        title = driver.title
        html_length = len(driver.page_source)
        
        print(f"   Page title: {title}")
        print(f"   HTML length: {html_length}")
        
        # Save HTML for inspection
        with open('test_maps.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("   Saved HTML to test_maps.html")
        
        driver.quit()
        
        if html_length > 10000:
            print("✅ Google Maps loaded successfully")
        else:
            print("❌ Google Maps didn't load properly")
            
    except Exception as e:
        print(f"❌ Google Maps test error: {e}")
    
    print("\n=== DEBUG COMPLETE ===")
    print("Check test_maps.html to see what was actually loaded")

if __name__ == "__main__":
    test_everything()