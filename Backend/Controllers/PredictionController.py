from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import os
import joblib
from sqlalchemy.orm import Session
from Models.prediction import Prediction
from Controllers.MatchController import MatchBase
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score
from datetime import datetime

# ============================================
# MODEL CONFIGURATION - CHANGE THIS TO SWITCH MODELS
# ============================================
SELECTED_MODEL = "rf_rolling"  # ← Change this to switch models

# Available models:
# - "rf_basic"              → Basic Random Forest (60% accuracy)
# - "rf_rolling"            → RF + Rolling Features (68% accuracy) BEST
# - "logistic_regression"   → Logistic Regression (62% accuracy)
# - "svm"                   → Support Vector Machine (62% accuracy)
# - "xgboost"               → XGBoost (64% accuracy)
# ============================================

# Model metadata
MODEL_INFO = {
    "rf_basic": {
        "name": "Basic Random Forest",
        "file": "rf_basic.pkl",
        "predictors_key": "basic_predictors",
        "uses_rolling": False
    },
    "rf_rolling": {
        "name": "Random Forest with Rolling Features",
        "file": "rf_rolling.pkl",
        "predictors_key": "rolling_predictors",
        "uses_rolling": True
    },
    "logistic_regression": {
        "name": "Logistic Regression",
        "file": "logistic_regression.pkl",
        "predictors_key": "rolling_predictors",
        "uses_rolling": True
    },
    "svm": {
        "name": "Support Vector Machine",
        "file": "svm.pkl",
        "predictors_key": "rolling_predictors",
        "uses_rolling": True
    },
    "xgboost": {
        "name": "XGBoost",
        "file": "xgboost.pkl",
        "predictors_key": "rolling_predictors",
        "uses_rolling": True
    }
}

# Global cache for model
_cached_model = None
_cached_predictors = None
_cached_metrics = None
_cached_model_name = None

# Function for loading trained models so we can test different models with the predictor website
def load_trained_model():
    """Load the pre-trained model based on SELECTED_MODEL (loads once, cached)"""
    global _cached_model, _cached_predictors, _cached_metrics, _cached_model_name
    
    # Check if we need to reload (model changed)
    if _cached_model is not None and _cached_model_name == SELECTED_MODEL:
        # Return the specific model's metrics, not the full dictionary
        if SELECTED_MODEL not in _cached_metrics:
            raise KeyError(f"Model '{SELECTED_MODEL}' not found in cached metrics. Available: {list(_cached_metrics.keys())}")
        
        model_metrics = _cached_metrics[SELECTED_MODEL]
        
        # Validate metrics structure
        if 'accuracy' not in model_metrics or 'precision' not in model_metrics:
            raise KeyError(f"Cached metrics for '{SELECTED_MODEL}' missing required keys. Found: {list(model_metrics.keys())}")
        
        return _cached_model, _cached_predictors, model_metrics
    
    # Clear cache if model changed
    if _cached_model_name != SELECTED_MODEL:
        _cached_model = None
        _cached_predictors = None
        _cached_metrics = None
    
    try:
        # Validate selected model
        if SELECTED_MODEL not in MODEL_INFO:
            raise ValueError(f"Invalid model '{SELECTED_MODEL}'. Available: {list(MODEL_INFO.keys())}")
        
        model_config = MODEL_INFO[SELECTED_MODEL]
        
        # Get path to saved models - try multiple paths for Docker and local
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        possible_models_dirs = [
            "/app/MachineLearning/models",  # Docker path
            os.path.join(parent_dir, "../MachineLearning/models"),  # Local relative path
            os.path.join(script_dir, "../MachineLearning/models"),
            "MachineLearning/models"
        ]
        
        models_dir = None
        for path in possible_models_dirs:
            test_path = os.path.join(path, model_config["file"])
            if os.path.exists(test_path):
                models_dir = path
                break
        
        if not models_dir:
            raise FileNotFoundError(f"Model directory not found. Tried: {possible_models_dirs}")
        
        # Load model based on SELECTED_MODEL
        model_path = os.path.join(models_dir, model_config["file"])
        
        # Determine predictors file based on model config
        if model_config["uses_rolling"]:
            predictors_path = os.path.join(models_dir, "rolling_predictors.pkl")
        else:
            predictors_path = os.path.join(models_dir, "basic_predictors.pkl")
        
        metrics_path = os.path.join(models_dir, "all_metrics.pkl")
        
        print(f" Loading model: {model_config['name']}")
        print(f"   File: {model_path}")
        
        _cached_model = joblib.load(model_path)
        _cached_predictors = joblib.load(predictors_path)
        _cached_metrics = joblib.load(metrics_path)
        _cached_model_name = SELECTED_MODEL
        
        # Get metrics for this model
        if SELECTED_MODEL not in _cached_metrics:
            raise KeyError(f"Model '{SELECTED_MODEL}' not found in metrics file. Available: {list(_cached_metrics.keys())}")
        
        metrics = _cached_metrics[SELECTED_MODEL]
        
        # Validate metrics structure
        if 'accuracy' not in metrics or 'precision' not in metrics:
            raise KeyError(f"Metrics for '{SELECTED_MODEL}' missing required keys. Found: {list(metrics.keys())}")
        
        acc = metrics['accuracy']
        prec = metrics['precision']
        
        print(f" Model loaded successfully!")
        print(f"   Accuracy: {acc:.4f}, Precision: {prec:.4f}")
        
        return _cached_model, _cached_predictors, metrics
        
    except FileNotFoundError as e:
        print(f" Model file not found: {e}")
        print(" Falling back to training new model...")
        return None, None, None
    except Exception as e:
        print(f" Error loading model: {e}")
        return None, None, None


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

#API call get request to get all predictions
async def readAllPredictions(db:Session):
    predictions = db.query(Prediction).all()
    if predictions is None:
        raise HTTPException(status_code=404,detail="No predictions found")
    return predictions

#API call get request to get all predictions for a specific team
async def readPredictionPerTeam(teamName:str, db:Session):
    predictions = db.query(Prediction).filter(Prediction.home_team == teamName).all()
    if predictions is None:
        raise HTTPException(status_code=404, detail='No predictions found')
    return predictions

#function to load the 2025-2026 schedule
def load2025Schedule():

    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Try multiple paths in case running in Docker or locally
    possible_paths = [
        "/app/WebScraper/schedules_2025_2026.csv",  # Docker path
        os.path.join(script_dir, "../../WebScraper/schedules_2025_2026.csv"),  # Local relative path
        os.path.join(script_dir, "../WebScraper/schedules_2025_2026.csv"),
        "WebScraper/schedules_2025_2026.csv"
    ]
    
    schedule_path = None
    for path in possible_paths:
        if os.path.exists(path):
            schedule_path = path
            break
    
    if not schedule_path:
        raise FileNotFoundError(f"schedules_2025_2026.csv not found in expected locations. Tried: {possible_paths}")

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

#API call post request to predict the outcome of a match
async def predictMatchOutcome(match: MatchBase, db: Session):
    try:

        # Get path to 2020-2022 matches.csv
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Try multiple paths in case running in Docker or locally
        possible_paths = [
            os.path.join(script_dir, "../../MachineLearning/matches.csv"),
            os.path.join(script_dir, "../MachineLearning/matches.csv"),
            "/app/MachineLearning/matches.csv",
            "MachineLearning/matches.csv"
        ]
        
        matches_path = None
        for path in possible_paths:
            if os.path.exists(path):
                matches_path = path
                break
        
        if not matches_path:
            return {"error": "matches.csv not found in expected locations"}
        
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

        # Calculate rolling averages for 2020-2022 data (only needed for fallback training)
        matches_rolling = matches.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
        matches_rolling = matches_rolling.droplevel('team')
        matches_rolling.index = range(matches_rolling.shape[0])

        # Load pre-trained model (MUCH FASTER!)
        rf, predictors, metrics = load_trained_model()
        
        if rf is None:
            # Fallback: train new model if saved model not found
            print("⚠️  Training new model (saved model not available)...")
            rf = RandomForestClassifier(n_estimators=100, min_samples_split=10, random_state=42)
            
            train = matches_rolling[matches_rolling["date"] < '2022-01-01']
            test = matches_rolling[matches_rolling["date"] >= '2022-01-01']
            predictors = ["h/a", "opp", "hour", "day"] + new_cols
            
            rf.fit(train[predictors], train["target"])
            
            preds = rf.predict(test[predictors])
            acc = accuracy_score(test["target"], preds)
            precision = precision_score(test["target"], preds)
        else:
            # Use metrics from loaded model
            acc = metrics['accuracy']
            precision = metrics['precision']

        ####################### END OF EDITS #####################
        
        # Load 2025 season data
        completed_2025 = load2025Schedule()
        
        # Calculate rolling averages for 2025 data
        completed_2025_rolling = completed_2025.groupby("team").apply(
            lambda x: rolling_averages(x, cols, new_cols)
        )
        completed_2025_rolling = completed_2025_rolling.droplevel('team')
        completed_2025_rolling.index = range(completed_2025_rolling.shape[0])

        # Clean time string - remove parentheses and extra spaces
        clean_time = match.time.split("(")[0].strip() if match.time else ""
        # Extract just the time part (HH:MM format)
        if " " in clean_time:
            clean_time = clean_time.split(" ")[0]
        
        # Default to noon if time is missing or invalid
        if not clean_time or ":" not in clean_time:
            clean_time = "12:00"

        try:
            match_datetime = pd.to_datetime(f"{match.date} {clean_time}")
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid time format: '{match.time}'. Parsed as '{clean_time}'. Error: {str(e)}"
         )

        # Check if teams exist in the schedule data
        available_teams = completed_2025['team'].unique().tolist()
        
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
        
        # Better error messages
        if len(home_data) == 0:
            # Check if team exists in schedule at all
            if match.team_name not in available_teams:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Team '{match.team_name}' not found in schedule data. Available teams: {', '.join(sorted(available_teams)[:10])}..."
                )
            # Check if team has matches before this date
            home_matches_before = completed_2025[
                (completed_2025['team'] == match.team_name) &
                (completed_2025['date'] < match_datetime)
            ]
            if len(home_matches_before) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"No completed matches found for {match.team_name} before {match.date}. Need at least 3 completed matches to calculate rolling averages."
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Not enough completed matches for {match.team_name} before {match.date}. Found {len(home_matches_before)} match(es), but need at least 3 for rolling averages."
                )
        
        if len(away_data) == 0:
            # Check if team exists in schedule at all
            if match.opponent not in available_teams:
                raise HTTPException(
                    status_code=404,
                    detail=f"Team '{match.opponent}' not found in schedule data. Available teams: {', '.join(sorted(available_teams)[:10])}..."
                )
            # Check if team has matches before this date
            away_matches_before = completed_2025[
                (completed_2025['team'] == match.opponent) &
                (completed_2025['date'] < match_datetime)
            ]
            if len(away_matches_before) == 0:
                raise HTTPException(
                    status_code=404,
                    detail=f"No completed matches found for {match.opponent} before {match.date}. Need at least 3 completed matches to calculate rolling averages."
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"Not enough completed matches for {match.opponent} before {match.date}. Found {len(away_matches_before)} match(es), but need at least 3 for rolling averages."
                )
        
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
        try:
            match_hour = int(clean_time.split(':')[0])
        except (ValueError, AttributeError):
            match_hour = 12  # Default to noon if parsing fails
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