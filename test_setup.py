"""
Test script to verify the setup and dependencies
Run this script to check if all components are working correctly
"""

import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
    except ImportError as e:
        print(f"❌ Selenium import failed: {e}")
        return False
    
    try:
        import crawl4ai
        print("✅ Crawl4AI imported successfully")
    except ImportError as e:
        print(f"❌ Crawl4AI import failed: {e}")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment setup"""
    print("\n🌍 Testing environment...")
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check for Gemini API key
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv('GEMINI_API_KEY'):
            print("✅ GEMINI_API_KEY found in environment")
        else:
            print("⚠️ GEMINI_API_KEY not found in .env file")
            return False
    else:
        print("❌ .env file not found")
        print("   Please create a .env file with your GEMINI_API_KEY")
        return False
    
    return True

def test_chrome_driver():
    """Test Chrome driver setup"""
    print("\n🌐 Testing Chrome driver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background for testing
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test basic functionality
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        if "Google" in title:
            print("✅ Chrome driver working correctly")
            return True
        else:
            print("❌ Chrome driver test failed")
            return False
            
    except Exception as e:
        print(f"❌ Chrome driver setup failed: {e}")
        return False

def test_project_structure():
    """Test project file structure"""
    print("\n📁 Testing project structure...")
    
    required_files = [
        'app.py',
        'requirements.txt',
        '.env',
        'src/crawl4ai_scraper.py',
        'src/csv_analyzer.py'
    ]
    
    required_dirs = [
        'src',
        'data'
    ]
    
    # Check directories
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ Directory '{dir_name}' found")
        else:
            print(f"❌ Directory '{dir_name}' missing")
            if dir_name == 'data':
                os.makedirs(dir_name, exist_ok=True)
                print(f"✅ Created directory '{dir_name}'")
    
    # Check files
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File '{file_path}' found")
        else:
            print(f"❌ File '{file_path}' missing")
            all_files_exist = False
    
    return all_files_exist

def main():
    """Run all tests"""
    print("🚀 Google Review Analyser - Setup Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 4
    
    # Test imports
    if test_imports():
        tests_passed += 1
    
    # Test environment
    if test_environment():
        tests_passed += 1
    
    # Test project structure
    if test_project_structure():
        tests_passed += 1
    
    # Test Chrome driver (optional, might take time)
    print("\n🤔 Test Chrome driver? (This might take a minute) [y/N]: ", end="")
    test_chrome = input().lower().strip() == 'y'
    
    if test_chrome:
        if test_chrome_driver():
            tests_passed += 1
    else:
        print("⏭️ Skipping Chrome driver test")
        total_tests -= 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n🚀 To start the application, run:")
        print("   streamlit run app.py")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("\n📋 Setup checklist:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Create .env file with GEMINI_API_KEY")
        print("   3. Ensure Chrome browser is installed")

if __name__ == "__main__":
    main()