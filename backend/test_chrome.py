#!/usr/bin/env python3
"""
Test script to verify Chrome setup in Docker environment
"""
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def test_chrome_setup():
    """Test Chrome setup for Docker deployment"""
    print("🧪 Testing Chrome setup for Docker deployment...")
    
    # Check if we're in a Docker environment
    is_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER')
    print(f"Docker environment detected: {is_docker}")
    
    # Check for Chrome binary
    chrome_paths = [
        os.getenv('CHROME_BIN'),
        os.getenv('GOOGLE_CHROME_BIN'),
        '/usr/bin/google-chrome-stable',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser'
    ]
    
    chrome_binary = None
    for path in chrome_paths:
        if path and os.path.exists(path):
            chrome_binary = path
            print(f"✅ Found Chrome at: {path}")
            break
    
    if not chrome_binary:
        print("❌ No Chrome binary found!")
        return False
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.binary_location = chrome_binary
    
    try:
        # Try WebDriver Manager setup
        print("📦 Testing WebDriver Manager setup...")
        driver_path = ChromeDriverManager().install()
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Test basic functionality
        print("🌐 Testing navigation...")
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Page title: {title}")
        
        driver.quit()
        print("✅ Chrome setup test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ Chrome setup test FAILED: {e}")
        return False

if __name__ == "__main__":
    success = test_chrome_setup()
    sys.exit(0 if success else 1)
