import pandas as pd 
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, accuracy_score
import os

# get path to matches.csv
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
matches_path = os.path.join(parent_dir, "MachineLearning", "matches.csv")
matches = pd.read_csv(matches_path, index_col=0)

print("team1 VS team2 MATCH PREDICTOR")
print("Using Random Forest Model")

matches["date"] = pd.to_datetime(matches["date"])
matches["h/a"] = matches["venue"].astype("category").cat.codes
matches["opp"] = matches["opponent"].astype("category").cat.codes
matches["hour"] = matches["time"].str.replace(":.+", "", regex=True).astype("int")
matches["day"] = matches["date"].dt.dayofweek
matches["target"] = (matches["result"] == "W").astype("int")

# ===== ROLLING AVERAGES FUNCTION =====
def rolling_averages(group, cols, new_cols):
    group = group.sort_values("date")
    rolling_stats = group[cols].rolling(3, closed='left').mean()
    group[new_cols] = rolling_stats
    group = group.dropna(subset=new_cols)
    print("hi")
    return group

cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{c}_rolling" for c in cols]

print("\nCalculating rolling averages (last 3 matches for each team)")
matches_rolling = matches.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
matches_rolling = matches_rolling.droplevel('team')
matches_rolling.index = range(matches_rolling.shape[0])

# training model on data before 2022
print("\nTraining Random Forest Classifier")
rf = RandomForestClassifier(n_estimators=100, min_samples_split=10, random_state=1)

# Split: train on data before 2022, test on 2022 onwards
train = matches_rolling[matches_rolling["date"] < '2022-01-01']
test = matches_rolling[matches_rolling["date"] >= '2022-01-01']

predictors = ["h/a", "opp", "hour", "day"] + new_cols

rf.fit(train[predictors], train["target"])

# Test accuracy
preds = rf.predict(test[predictors])
acc = accuracy_score(test["target"], preds)
precision = precision_score(test["target"], preds)

print(f" Model trained on {len(train)} matches")
print(f" Test accuracy: {acc:.2%}")
print(f" Test precision: {precision:.2%}")

# Arsenal 2025 data
arsenal_2025 = pd.DataFrame({
    'date': ['2025-08-17', '2025-08-23', '2025-08-31', '2025-09-13', '2025-09-21', 
             '2025-09-28', '2025-10-04', '2025-10-18', '2025-10-26', '2025-11-01', '2025-11-08'],
    'time': ['16:30', '17:30', '16:30', '12:30', '16:30', '16:30', '15:00', '16:30', '14:00', '15:00', '16:30'],
    'venue': ['Away', 'Home', 'Away', 'Home', 'Home', 'Away', 'Home', 'Away', 'Home', 'Away', 'Away'],
    'result': ['W', 'W', 'L', 'W', 'D', 'W', 'W', 'W', 'W', 'W', 'D'],
    'gf': [1, 5, 0, 3, 1, 2, 2, 1, 1, 2, 2],
    'ga': [0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 2],
    'opponent': ['Manchester Utd', 'Leeds United', 'Liverpool', 'Nottingham Forest', 'Manchester City',
                 'Newcastle Utd', 'West Ham', 'Fulham', 'Crystal Palace', 'Burnley', 'Sunderland'],
    'team': ['Arsenal'] * 11,
    'sh': [15, 20, 8, 18, 14, 16, 17, 12, 13, 16, 15],
    'sot': [6, 10, 3, 8, 5, 7, 8, 5, 6, 7, 6],
    'dist': [18, 16, 20, 17, 19, 18, 17, 19, 18, 17, 18],
    'fk': [2, 1, 3, 2, 2, 1, 2, 3, 2, 1, 2],
    'pk': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'pkatt': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'season': [2025] * 11
})

# Tottenham 2025 data
tottenham_2025 = pd.DataFrame({
    'date': ['2025-08-16', '2025-08-23', '2025-08-30', '2025-09-13', '2025-09-20', 
             '2025-09-27', '2025-10-04', '2025-10-19', '2025-10-26', '2025-11-01', '2025-11-08'],
    'time': ['15:00', '12:30', '15:00', '17:30', '15:00', '20:00', '12:30', '14:00', '16:30', '17:30', '12:30'],
    'venue': ['Home', 'Away', 'Home', 'Away', 'Away', 'Home', 'Away', 'Home', 'Away', 'Home', 'Home'],
    'result': ['W', 'W', 'L', 'W', 'D', 'D', 'W', 'L', 'W', 'L', 'D'],
    'gf': [3, 2, 0, 3, 2, 1, 2, 1, 3, 0, 2],
    'ga': [0, 0, 1, 0, 2, 1, 1, 2, 0, 1, 2],
    'opponent': ['Burnley', 'Manchester City', 'Bournemouth', 'West Ham', 'Brighton',
                 'Wolves', 'Leeds United', 'Aston Villa', 'Everton', 'Chelsea', 'Manchester Utd'],
    'team': ['Tottenham'] * 11,
    'sh': [18, 12, 8, 16, 14, 10, 13, 11, 17, 7, 13],
    'sot': [9, 5, 3, 7, 6, 4, 6, 5, 8, 2, 6],
    'dist': [17, 19, 21, 18, 19, 20, 18, 20, 17, 22, 19],
    'fk': [1, 2, 3, 2, 3, 2, 2, 3, 1, 2, 2],
    'pk': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'pkatt': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'season': [2025] * 11
})

# Combine 2025 data
new_data = pd.concat([arsenal_2025, tottenham_2025], ignore_index=True)
new_data["date"] = pd.to_datetime(new_data["date"])
new_data["h/a"] = new_data["venue"].map({'Home': 1, 'Away': 0})
new_data["opp"] = new_data["opponent"].astype("category").cat.codes
new_data["hour"] = new_data["time"].str.replace(":.+", "", regex=True).astype("int")
new_data["day"] = new_data["date"].dt.dayofweek
new_data["target"] = (new_data["result"] == "W").astype("int")

# Calculate rolling averages for 2025 data
new_data_rolling = new_data.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
new_data_rolling = new_data_rolling.droplevel('team')
new_data_rolling.index = range(new_data_rolling.shape[0])

# Get latest stats for both teams
arsenal_latest = new_data_rolling[new_data_rolling["team"] == "Arsenal"].sort_values("date").iloc[-1]
tottenham_latest = new_data_rolling[new_data_rolling["team"] == "Tottenham"].sort_values("date").iloc[-1]


# Get opponent code for Tottenham from historical data
tottenham_opp_code = matches[matches["opponent"].str.contains("Tottenham", case=False, na=False)]["opp"].mode()[0] if len(matches[matches["opponent"].str.contains("Tottenham", case=False, na=False)]) > 0 else 15

arsenal_match = pd.DataFrame({
    "h/a": [1],
    "opp": [tottenham_opp_code],
    "hour": [16],
    "day": [6],
})

for col in new_cols:
    arsenal_match[col] = arsenal_latest[col]

arsenal_pred = rf.predict(arsenal_match)[0]
arsenal_prob = rf.predict_proba(arsenal_match)[0]

print(f"\n Arsenal's Recent Form (3-match rolling avg):")
print(f"   Goals For: {arsenal_latest['gf_rolling']:.2f}")
print(f"   Goals Against: {arsenal_latest['ga_rolling']:.2f}")
print(f"   Shots: {arsenal_latest['sh_rolling']:.2f}")
print(f"   Shots on Target: {arsenal_latest['sot_rolling']:.2f}")

print(f"\n Random Forest Prediction:")
print(f"   Arsenal Win: {arsenal_prob[1]:.2%}")
print(f"   Arsenal Not Win: {arsenal_prob[0]:.2%}")
print(f"   Prediction: {' WIN' if arsenal_pred == 1 else ' NOT WIN'}")


arsenal_opp_code = matches[matches["opponent"].str.contains("Arsenal", case=False, na=False)]["opp"].mode()[0] if len(matches[matches["opponent"].str.contains("Arsenal", case=False, na=False)]) > 0 else 0

tottenham_match = pd.DataFrame({
    "h/a": [0],
    "opp": [arsenal_opp_code],
    "hour": [16],
    "day": [6],
})

for col in new_cols:
    tottenham_match[col] = tottenham_latest[col]

tottenham_pred = rf.predict(tottenham_match)[0]
tottenham_prob = rf.predict_proba(tottenham_match)[0]

print(f"\n Tottenham's Recent Form (3-match rolling avg):")
print(f"   Goals For: {tottenham_latest['gf_rolling']:.2f}")
print(f"   Goals Against: {tottenham_latest['ga_rolling']:.2f}")
print(f"   Shots: {tottenham_latest['sh_rolling']:.2f}")
print(f"   Shots on Target: {tottenham_latest['sot_rolling']:.2f}")

print(f"\n Random Forest Prediction:")
print(f"   Tottenham Win: {tottenham_prob[1]:.2%}")
print(f"   Tottenham Not Win: {tottenham_prob[0]:.2%}")
print(f"   Prediction: {' WIN' if tottenham_pred == 1 else ' NOT WIN'}")

# Calculate probabilities
arsenal_win = arsenal_prob[1]
tottenham_win = tottenham_prob[1]

# Estimate draw probability
if arsenal_win + tottenham_win > 1.0:
    draw_prob = 0.25
    total = arsenal_win + tottenham_win + draw_prob
    arsenal_win = arsenal_win / total
    tottenham_win = tottenham_win / total
    draw_prob = draw_prob / total
else:
    draw_prob = 1 - arsenal_win - tottenham_win

print(f"\n WIN PROBABILITIES:")
print(f"   Arsenal Win:    {arsenal_win:.2%}")
print(f"   Draw:           {draw_prob:.2%}")
print(f"   Tottenham Win:  {tottenham_win:.2%}")

# Score prediction - adjusted based on win probabilities
base_arsenal = (arsenal_latest['gf_rolling'] * 0.7 + tottenham_latest['ga_rolling'] * 0.3) * 1.05
base_tottenham = (tottenham_latest['gf_rolling'] * 0.7 + arsenal_latest['ga_rolling'] * 0.3) * 0.95

# Adjust scores based on who's more likely to win
if arsenal_win > tottenham_win + 0.15:  # Arsenal strongly favored
    arsenal_score = max(1, round(base_arsenal + 0.3))
    tottenham_score = max(0, round(base_tottenham - 0.2))
elif tottenham_win > arsenal_win + 0.15:  # Tottenham strongly favored
    arsenal_score = max(0, round(base_arsenal - 0.2))
    tottenham_score = max(1, round(base_tottenham + 0.3))
else:  # Close match - could be draw
    arsenal_score = round(base_arsenal)
    tottenham_score = round(base_tottenham)

print(f"\n PREDICTED SCORE: Arsenal {arsenal_score} - {tottenham_score} Tottenham")

print("\n final result")
if arsenal_win > tottenham_win and arsenal_win > draw_prob:
    print(f"ARSENAL TO WIN (Confidence: {arsenal_win:.1%})")
elif tottenham_win > arsenal_win and tottenham_win > draw_prob:
    print(f"TOTTENHAM TO WIN (Confidence: {tottenham_win:.1%})")
elif draw_prob > arsenal_win and draw_prob > tottenham_win:
    print(f"DRAW LIKELY (Probability: {draw_prob:.1%})")
else:
    print(f"CLOSE MATCH")

print(arsenal_match)
print(tottenham_match)