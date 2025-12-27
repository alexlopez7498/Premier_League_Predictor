@echo off
REM Batch file to run the scraper scheduler
REM This can be used with Windows Task Scheduler

cd /d "%~dp0"
cd ..

REM Activate virtual environment if it exists (uncomment if you use venv)
REM call venv\Scripts\activate.bat

REM Run the scheduler
python WebScraper\scheduler.py

REM Keep window open if there's an error (optional - remove if you want it to close)
if errorlevel 1 (
    pause
)

