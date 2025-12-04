from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in background
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# create the driver
driver = webdriver.Chrome(options=chrome_options)

try:
    print("Loading Premier League standings page...")
    driver.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    
    # Wait for the table to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'stats_table')))
    
    print("Parsing table...")
    
    # Parse with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    
    # Find the standings table (first stats_table)
    tables = soup.find_all('table', class_='stats_table')
    
    if not tables:
        print(" No tables found on the page")
        exit()
    
    # Get the first table (league standings)
    standings_table = tables[0]
    
    # Convert to DataFrame using pandas
    table_df = pd.read_html(str(standings_table))[0]
    
    # Handle multi-level columns if they exist
    if isinstance(table_df.columns, pd.MultiIndex):
        table_df.columns = table_df.columns.droplevel(0)
    
    # Display first few rows
    print("\nPreview of the table:")
    print(table_df.head())
    
    # Save to CSV
    table_df.to_csv("WebScraper/table.csv", index=False)
    print(f"\n Successfully saved to WebScraper/table.csv")

except Exception as e:
    print(f" Error occurred: {e}")

finally:
    driver.quit()
    print("\nBrowser closed")