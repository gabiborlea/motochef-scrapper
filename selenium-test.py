from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import platform
import time
from crawl4ai import AsyncWebCrawler
import asyncio

async def get_markdown(url, title):
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        try: 
            f = open('markdowns/' + title + '.md', 'x')
            f.write(result.markdown)
            #save to file
            f.close()
        except Exception:
            print('error')

class WebScraper:
    def __init__(self):
        # Initialize Chrome options
        self.chrome_options = webdriver.ChromeOptions()
        
        # Add headers and configurations to avoid detection
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent
        self.chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Initialize the Chrome WebDriver with proper architecture detection
        if platform.processor() == 'arm':
            # For M1/M2/M3 Macs
            self.chrome_options.add_argument('--no-sandbox')
            self.chrome_options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            service = Service()
            self.driver = webdriver.Chrome(
                service=service,
                options=self.chrome_options
            )
        else:
            # For other architectures
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=self.chrome_options
            )
        
        # Execute CDP commands to prevent detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Remove webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def scrape_website(self, url):
        try:
            # Navigate to the URL
            self.driver.get(url)
            
            # Wait for content to load (adjust selector as needed)
            wait = WebDriverWait(self.driver, 10)
            body = wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Extract the content
            print("Content found:")
            
            links = body.find_elements(By.TAG_NAME, "h4")
            for link in links:
                a_tag = link.find_element(By.TAG_NAME, "a")
                url = a_tag.get_attribute("href")
                title = a_tag.text
                asyncio.run(get_markdown(url, title))
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        
    def close(self):
        self.driver.quit()

def main():
    scraper = WebScraper()
    try:
        url = "https://rennlist.com/forums/cayenne-9y0-2019-247/"
        scraper.scrape_website(url)
    finally:
        scraper.close()

if __name__ == "__main__":
    main()