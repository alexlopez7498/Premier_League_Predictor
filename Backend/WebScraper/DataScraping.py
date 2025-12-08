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

# Initialize the driver
driver = webdriver.Chrome(options=chrome_options)

all_teams = []
all_schedules = []

try:
    # Get the main page
    print("Loading main page...")
    driver.get('https://fbref.com/en/comps/9/Premier-League-Stats')
    
    # Wait for the table to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'stats_table')))
    
    # Parse with BeautifulSoup
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # table to have all names standardized
    TEAM_NAME_MAP = {
    "Brighton and Hove Albion": "Brighton",
    "Brighton & Hove Albion": "Brighton",
    "Tottenham Hotspur": "Tottenham",
    "Wolverhampton Wanderers": "Wolves",
    "Manchester United": "Manchester Utd",
    "Newcastle United": "Newcastle Utd",
    "West Ham United": "West Ham",
    "Nottingham Forest": "Nott'ham Forest"
    }

    tables = soup.find_all('table', class_='stats_table')
    if not tables:
        print("No tables found")
        exit()
    
    table = tables[0]
    links = table.find_all('a')
    links = [l.get("href") for l in links if l.get("href")]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]
    
    print(f"Found {len(team_urls)} teams to scrape\n")
    
    for i, team_url in enumerate(team_urls, 1):
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        team_name = TEAM_NAME_MAP.get(team_name, team_name)
        
        print(f"Scraping {i}/{len(team_urls)}: {team_name}")
        
        # Scrape team stats
        try:
            driver.get(team_url)
            time.sleep(3)
            
            page_html = driver.page_source
            soup = BeautifulSoup(page_html, 'lxml')
            stats = soup.find_all('table', class_="stats_table")
            
            if not stats:
                print(f"  No stats table found for {team_name}, skipping...")
                continue
                
            stats = stats[0]
            team_data = pd.read_html(str(stats))[0]
            
            # Handle multi-level columns
            if isinstance(team_data.columns, pd.MultiIndex):
                team_data.columns = team_data.columns.droplevel()
            
            # Filter out rows where Player column is blank or contains header-like values
            player_col = team_data.columns[0]  # First column should be Player
            team_data = team_data[team_data[player_col].notna()]  # Remove NaN values
            team_data = team_data[team_data[player_col] != player_col]  # Remove header rows
            team_data = team_data[team_data[player_col].astype(str).str.strip() != '']  # Remove empty strings
            
            # Only add if there are valid player rows remaining
            if len(team_data) > 0:
                team_data["Team"] = team_name
                all_teams.append(team_data)
                print(f"Successfully scraped stats for {team_name} - {len(team_data)} players")
            else:
                print(f"No valid player data found for {team_name}")
            
        except Exception as e:
            print(f"Error scraping stats for {team_name}: {e}")
        
        # Scrape team schedule
        try:
            # Extract squad ID from the team URL
            squad_id = team_url.split("/squads/")[1].split("/")[0]
            
            # Construct schedule URL
            team_name_formatted = team_name.replace(" ", "-")
            schedule_url = f"https://fbref.com/en/squads/{squad_id}/2025-2026/matchlogs/c9/schedule/{team_name_formatted}-Scores-and-Fixtures-Premier-League"
            
            print(f"  Loading schedule from: {schedule_url}")
            driver.get(schedule_url)
            time.sleep(3)
            
            schedule_html = driver.page_source
            schedule_soup = BeautifulSoup(schedule_html, 'lxml')
            
            # Find the scores and fixtures table
            schedule_tables = schedule_soup.find_all('table', class_="stats_table")
            
            if schedule_tables:
                # Usually the first table contains the schedule
                schedule_table = schedule_tables[0]
                schedule_data = pd.read_html(str(schedule_table))[0]
                schedule_data = schedule_data[schedule_data[schedule_data.columns[0]] != schedule_data.columns[0]]
                
                # Handle multi-level columns
                if isinstance(schedule_data.columns, pd.MultiIndex):
                    schedule_data.columns = schedule_data.columns.droplevel(0)
                
                schedule_data["Team"] = team_name
                all_schedules.append(schedule_data)
                print(f"  ✓ Successfully scraped schedule for {team_name}")
            else:
                print(f"  ⚠ No schedule table found for {team_name}")
                
        except Exception as e:
            print(f"  ✗ Error scraping schedule for {team_name}: {e}")
        
        time.sleep(5)  # Be respectful to the server
    
    # Save stats data
    if all_teams:
        stat_df = pd.concat(all_teams, ignore_index=True)
        
        # Final cleanup: remove any rows where Player column is blank, NaN, or contains "Playing Time" etc.
        player_col = stat_df.columns[0]
        stat_df = stat_df[stat_df[player_col].notna()]
        stat_df = stat_df[stat_df[player_col].astype(str).str.strip() != '']
        stat_df = stat_df[~stat_df[player_col].astype(str).str.contains('Playing Time|Performance|Expected|Progression|Per 90 Minutes', na=False)]
        
        stat_df.to_csv("WebScraper/stats.csv", index=False)
        print(f"\nSuccessfully saved stats for {len(all_teams)} teams to stats.csv")
        print(f"Total players: {len(stat_df)}")
    else:
        print("\nNo stats data was scraped")
    
    # Save schedule data
    if all_schedules:
        schedule_df = pd.concat(all_schedules, ignore_index=True)
        schedule_df.to_csv("WebScraper/schedules_2025_2026.csv", index=False)
        print(f"Successfully saved schedules for {len(all_schedules)} teams to schedules_2025_2026.csv")
    else:
        print("No schedule data was scraped")

finally:
    driver.quit()
    print("\nBrowser closed")