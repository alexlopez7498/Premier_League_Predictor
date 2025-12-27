"""
Scheduler script to run DataScraping.py and LeagueTableScraping.py every 2 days.
Run this script to keep it running and automatically execute the scrapers.
"""
import schedule
import time
import subprocess
import sys
import os
from datetime import datetime

# Setup logging to file
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(LOG_DIR, "scheduler.log")

def log_message(message):
    """Log message to both console and file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    print(message)  # Also print to console
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Warning: Could not write to log file: {e}")

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)

def run_data_scraping():
    """Run the DataScraping.py script"""
    log_message("Starting DataScraping.py...")
    try:
        script_path = os.path.join(SCRIPT_DIR, "DataScraping.py")
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=BACKEND_DIR,
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            log_message("✓ DataScraping.py completed successfully")
        else:
            log_message(f"✗ DataScraping.py failed with return code {result.returncode}")
    except Exception as e:
        log_message(f"✗ Error running DataScraping.py: {e}")

def run_league_table_scraping():
    """Run the LeagueTableScraping.py script"""
    log_message("Starting LeagueTableScraping.py...")
    try:
        script_path = os.path.join(SCRIPT_DIR, "LeagueTableScraping.py")
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=BACKEND_DIR,
            capture_output=False,
            text=True
        )
        if result.returncode == 0:
            log_message("✓ LeagueTableScraping.py completed successfully")
        else:
            log_message(f"✗ LeagueTableScraping.py failed with return code {result.returncode}")
    except Exception as e:
        log_message(f"✗ Error running LeagueTableScraping.py: {e}")

def run_all_scrapers():
    """Run both scraping scripts"""
    log_message("="*60)
    log_message("Running scheduled scraping tasks...")
    log_message("="*60)
    
    # Run both scrapers sequentially
    run_data_scraping()
    time.sleep(2)  # Small delay between scripts
    run_league_table_scraping()
    
    log_message("All scraping tasks completed")
    log_message("="*60)

if __name__ == "__main__":
    log_message("="*60)
    log_message("Premier League Scraper Scheduler")
    log_message("="*60)
    log_message("This script will run DataScraping.py and LeagueTableScraping.py every 2 days.")
    log_message(f"Log file: {LOG_FILE}")
    log_message("Press Ctrl+C to stop the scheduler (if running interactively).\n")
    
    # Schedule the scraping tasks to run every 2 days
    schedule.every(2).days.do(run_all_scrapers)
    
    log_message("Running initial scrape...")
    run_all_scrapers()
    
    next_run = schedule.next_run()
    log_message(f"Next scheduled run: {next_run}")
    log_message("Scheduler is running...\n")
    
    # Keep the script running and check for scheduled tasks
    try:
        while True:
            schedule.run_pending()
            time.sleep(3600) 
    except KeyboardInterrupt:
        log_message("\nScheduler stopped by user.")
        sys.exit(0)
    except Exception as e:
        log_message(f"Fatal error in scheduler: {e}")
        sys.exit(1)

