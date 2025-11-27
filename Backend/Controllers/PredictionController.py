from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
from sqlalchemy.orm import Session
from Models.prediction import Prediction
from Controllers.MatchController import MatchBase
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score
from datetime import datetime

class PredictionBase(BaseModel):
    home_team: str
    away_team: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    predicted_score: str
    prediction: str
    confidence: float
    accuracy: float
    precision: float

async def readAllPredictions(db:Session):
    predictions = db.query(Prediction).all()
    if predictions is None:
        raise HTTPException(status_code=404,detail="No predictions found")
    return predictions

async def readPredictionPerTeam(teamName:str, db:Session):
    predictions = db.query(Prediction).filter(Prediction.home_team == teamName).all()
    if predictions is None:
        raise HTTPException(status_code=404, detail='No predictions found')
    return predictions

def load2025Schedule():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    schedule_path = os.path.join(script_dir, "../../WebScraper", "schedules_2025_2026.csv")

    schedule_df = pd.read_csv(schedule_path)

    # Filter completed matches only
    completed = schedule_df[schedule_df['Result'].notna()].copy()
    completed['date'] = pd.to_datetime(completed['Date'])
    completed['venue'] = completed['Venue']
    completed['result'] = completed['Result']
    completed['gf'] = completed['GF']
    completed['ga'] = completed['GA']
    completed['opponent'] = completed['Opponent']
    completed['team'] = completed['Team']

    # Fix time format
    completed['time'] = (
        completed['Time']
        .str.split('(').str[0]
        .str.strip()
        .str.split(' ').str[0]
    )

    # Add placeholder stats if missing, most new matches does not have detailed stats
    for stat in ['sh', 'sot', 'dist', 'fk', 'pk', 'pkatt']:
        if stat not in completed.columns:
            completed[stat] = 0  # Average placeholder
    
    return completed


async def predictMatchOutcome(match: MatchBase, db: Session):
    try:

        # Get path to 2020-2022 matches.csv
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        matches_path = os.path.join(parent_dir, "../MachineLearning", "matches.csv")
        matches = pd.read_csv(matches_path, index_col=0)

        # Preprocess 2020-2022 data
        matches["date"] = pd.to_datetime(matches["date"])
        matches["h/a"] = matches["venue"].astype("category").cat.codes
        matches["opp"] = matches["opponent"].astype("category").cat.codes
        matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int")
        matches["day"] = matches["date"].dt.dayofweek
        matches["target"] = (matches["result"] == "W").astype("int")

        # Rolling averages function
        def rolling_averages(group, cols, new_cols):
            group = group.sort_values("date")
            rolling_stats = group[cols].rolling(3, closed='left').mean()
            group[new_cols] = rolling_stats
            group = group.dropna(subset=new_cols)
            return group

        cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
        new_cols = [f"{c}_rolling" for c in cols]

        # Calculate rolling averages for 2020-2022 data
        matches_rolling = matches.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
        matches_rolling = matches_rolling.droplevel('team')
        matches_rolling.index = range(matches_rolling.shape[0])

        # Train Random Forest model
        rf = RandomForestClassifier(n_estimators=100, min_samples_split=10, random_state=1)
        
        train = matches_rolling[matches_rolling["date"] < '2022-01-01']
        test = matches_rolling[matches_rolling["date"] >= '2022-01-01']
        predictors = ["h/a", "opp", "hour", "day"] + new_cols
        
        rf.fit(train[predictors], train["target"])
        
        preds = rf.predict(test[predictors])
        acc = accuracy_score(test["target"], preds)
        precision = precision_score(test["target"], preds)
        
        # Load 2025 season data
        completed_2025 = load2025Schedule()
        
        # Calculate rolling averages for 2025 data
        completed_2025_rolling = completed_2025.groupby("team").apply(
            lambda x: rolling_averages(x, cols, new_cols)
        )
        completed_2025_rolling = completed_2025_rolling.droplevel('team')
        completed_2025_rolling.index = range(completed_2025_rolling.shape[0])

        clean_time = match.time.split("(")[0].strip()

        try:
            match_datetime = pd.to_datetime(f"{match.date} {clean_time}")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time format: '{match.time}'. Parsed as '{clean_time}'."
         )

        # Get latest stats for home team
        home_data = completed_2025_rolling[
            (completed_2025_rolling['team'] == match.team_name) &
            (completed_2025_rolling['date'] < match_datetime)
        ]
        
        # Get latest stats for away team
        away_data = completed_2025_rolling[
            (completed_2025_rolling['team'] == match.opponent) &
            (completed_2025_rolling['date'] < match_datetime)
        ]
        
        if len(home_data) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for {match.team_name}")
        if len(away_data) == 0:
            raise HTTPException(status_code=404, detail=f"No data found for {match.opponent}")
        
        home_latest = home_data.sort_values('date').iloc[-1]
        away_latest = away_data.sort_values('date').iloc[-1]

        # Get opponent codes from historical data only 2020-2022
        away_opp_code = matches[
            matches["opponent"].str.contains(match.opponent.split()[0], case=False, na=False)
        ]["opp"].mode()
        away_opp_code = away_opp_code[0] if len(away_opp_code) > 0 else 10
        
        home_opp_code = matches[
            matches["opponent"].str.contains(match.team_name.split()[0], case=False, na=False)
        ]["opp"].mode()
        home_opp_code = home_opp_code[0] if len(home_opp_code) > 0 else 10

        # Create prediction data for home team
        match_hour = int(match.time.split(':')[0])
        match_day = match_datetime.dayofweek
        
        home_match = pd.DataFrame({
            "h/a": [1],
            "opp": [away_opp_code],
            "hour": [match_hour],
            "day": [match_day],
        })
        
        for col in new_cols:
            home_match[col] = home_latest[col]
        
        home_pred = rf.predict(home_match)[0]
        home_prob = rf.predict_proba(home_match)[0]

        # Create prediction data for away team
        away_match = pd.DataFrame({
            "h/a": [0],
            "opp": [home_opp_code],
            "hour": [match_hour],
            "day": [match_day],
        })
        
        for col in new_cols:
            away_match[col] = away_latest[col]
        
        away_pred = rf.predict(away_match)[0]
        away_prob = rf.predict_proba(away_match)[0]

        # Calculate probabilities
        home_win = home_prob[1]
        away_win = away_prob[1]
        
        if home_win + away_win > 1.0:
            draw_prob = 0.25
            total = home_win + away_win + draw_prob
            home_win = home_win / total
            away_win = away_win / total
            draw_prob = draw_prob / total
        else:
            draw_prob = 1 - home_win - away_win

        # Score prediction, doesn't have to be accurate just indicative
        base_home = (home_latest['gf_rolling'] * 0.7 + away_latest['ga_rolling'] * 0.3) * 1.05
        base_away = (away_latest['gf_rolling'] * 0.7 + home_latest['ga_rolling'] * 0.3) * 0.95

        if home_win > away_win + 0.15:
            home_score = max(1, round(base_home + 0.3))
            away_score = max(0, round(base_away - 0.2))
        elif away_win > home_win + 0.15:
            home_score = max(0, round(base_home - 0.2))
            away_score = max(1, round(base_away + 0.3))
        else:
            home_score = round(base_home)
            away_score = round(base_away)

        # Store prediction in database
        predictionEntry = Prediction(
            home_team=match.team_name,
            away_team=match.opponent,
            home_win_prob=float(round(home_win, 4)),
            draw_prob=float(round(draw_prob, 4)),
            away_win_prob=float(round(away_win, 4)),
            predicted_score=f"{home_score}-{away_score}",
            confidence=float(round(max(home_win, away_win, draw_prob), 4)),
            predicted_winner=(match.team_name if home_win > away_win else (match.opponent if away_win > home_win else "Draw")),
            accuracy=float(round(acc, 4)),
            precision=float(round(precision, 4)),
        )

        db.add(predictionEntry)
        db.commit()

        #returns json object as the response
        return PredictionBase(
            home_team=predictionEntry.home_team,
            away_team=predictionEntry.away_team,
            home_win_prob=float(predictionEntry.home_win_prob),
            draw_prob=float(predictionEntry.draw_prob),
            away_win_prob=float(predictionEntry.away_win_prob),
            predicted_score=predictionEntry.predicted_score,
            prediction=predictionEntry.predicted_winner,
            confidence=float(predictionEntry.confidence),
            accuracy=float(predictionEntry.accuracy),
            precision=float(predictionEntry.precision)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))