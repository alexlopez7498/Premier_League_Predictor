# Premier League Predictor

An AI-powered web application that predicts Premier League match outcomes using machine learning and provides team analytics.

## Features

- **Match Predictions**: Machine learning model predicts match outcomes
- **Current Week Matches**: View upcoming matches grouped by day
- **Team Statistics**: Browse player stats and team performance metrics
- **League Table**: Real-time Premier League standings

## Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Machine Learning**: scikit-learn
- **Web Scraping**: Selenium + BeautifulSoup

### Frontend
- **Framework**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS

## Project Structure

```
├── backend/           # FastAPI application
│   ├── main.py       # App entry point
│   ├── database.py   # Database config
│   ├── Models/       # SQLAlchemy ORM models
│   └── Controllers/  # Business logic
├── frontend/          # Next.js application
│   └── src/
│       ├── app/      # Pages
│       └── components/ # React components
├── WebScraper/       # Data collection scripts
└── MachineLearning/  # ML models
```

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL 12+

### Installation

1. **Backend**:
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

1. **Start Backend**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload
   ```

2. **Start Frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open `http://localhost:3000` in your browser

## API Endpoints

- `GET /matches/current-week` - Get current week matches
- `GET /teams` - Get all teams
- `GET /players` - Get player statistics

## License

MIT License - See LICENSE file for details