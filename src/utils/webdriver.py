from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.config import settings

def setup_chrome_driver():
    """Set up Chrome driver with appropriate options"""
    chrome_options = Options()
    
    # Run in headless mode in production environment
    if settings.HEADLESS:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Set user agent to avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    return webdriver.Chrome(options=chrome_options)