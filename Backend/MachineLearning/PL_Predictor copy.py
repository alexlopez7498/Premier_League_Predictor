"""
PL Predictor - Model Comparison Script
Tests all saved models from ML_models.ipynb
"""
import pandas as pd 
import numpy as np
from sklearn.metrics import precision_score, accuracy_score, classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

print("="*70)
print("PREMIER LEAGUE MATCH PREDICTOR - MODEL COMPARISON")
print("="*70)

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.join(script_dir, "models")

# Load the data
print("\n📊 Loading data...")
matches = pd.read_csv(os.path.join(script_dir, "matches.csv"), index_col=0)

# Preprocess data
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

# Calculate rolling averages
cols = ["gf", "ga", "sh", "sot", "dist", "fk", "pk", "pkatt"]
new_cols = [f"{c}_rolling" for c in cols]

matches_rolling = matches.groupby("team").apply(lambda x: rolling_averages(x, cols, new_cols))
matches_rolling = matches_rolling.droplevel('team')
matches_rolling.index = range(matches_rolling.shape[0])

# Split data
train = matches_rolling[matches_rolling["date"] < '2022-01-01']
test = matches_rolling[matches_rolling["date"] > '2022-01-01']

basic_predictors = ["h/a", "opp", "hour", "day"]
rolling_predictors = basic_predictors + new_cols

print(f"✅ Data loaded: {len(train)} train, {len(test)} test samples")

# Check if models exist
if os.path.exists(models_dir):
    print(f"\n🤖 Loading saved models from: {models_dir}\n")
    
    try:
        # Load all models
        rf_basic = joblib.load(f'{models_dir}/rf_basic.pkl')
        rf_rolling = joblib.load(f'{models_dir}/rf_rolling.pkl')
        lr = joblib.load(f'{models_dir}/logistic_regression.pkl')
        svm_model = joblib.load(f'{models_dir}/svm.pkl')
        xgb = joblib.load(f'{models_dir}/xgboost.pkl')
        all_metrics = joblib.load(f'{models_dir}/all_metrics.pkl')
        
        print("✅ All models loaded successfully!")
        print(f"📅 Models saved at: {all_metrics['saved_at']}")
        
        # Test each model
        print("\n" + "="*70)
        print("MODEL PERFORMANCE ON TEST SET")
        print("="*70)
        
        results = []
        
        # 1. Basic Random Forest
        print("\n1️⃣  BASIC RANDOM FOREST")
        print("-" * 70)
        preds_basic = rf_basic.predict(test[basic_predictors])
        acc_basic = accuracy_score(test["target"], preds_basic)
        prec_basic = precision_score(test["target"], preds_basic)
        print(f"Accuracy:  {acc_basic:.4f} ({acc_basic*100:.2f}%)")
        print(f"Precision: {prec_basic:.4f} ({prec_basic*100:.2f}%)")
        results.append(("Basic RF", acc_basic, prec_basic))
        
        # 2. Random Forest + Rolling Features
        print("\n2️⃣  RANDOM FOREST + ROLLING FEATURES ⭐")
        print("-" * 70)
        preds_rolling = rf_rolling.predict(test[rolling_predictors])
        acc_rolling = accuracy_score(test["target"], preds_rolling)
        prec_rolling = precision_score(test["target"], preds_rolling)
        print(f"Accuracy:  {acc_rolling:.4f} ({acc_rolling*100:.2f}%)")
        print(f"Precision: {prec_rolling:.4f} ({prec_rolling*100:.2f}%)")
        results.append(("RF + Rolling", acc_rolling, prec_rolling))
        
        # 3. Logistic Regression
        print("\n3️⃣  LOGISTIC REGRESSION")
        print("-" * 70)
        preds_lr = lr.predict(test[rolling_predictors])
        acc_lr = accuracy_score(test["target"], preds_lr)
        prec_lr = precision_score(test["target"], preds_lr)
        print(f"Accuracy:  {acc_lr:.4f} ({acc_lr*100:.2f}%)")
        print(f"Precision: {prec_lr:.4f} ({prec_lr*100:.2f}%)")
        results.append(("Logistic Reg", acc_lr, prec_lr))
        
        # 4. SVM
        print("\n4️⃣  SUPPORT VECTOR MACHINE")
        print("-" * 70)
        preds_svm = svm_model.predict(test[rolling_predictors])
        acc_svm = accuracy_score(test["target"], preds_svm)
        prec_svm = precision_score(test["target"], preds_svm, zero_division=0)
        print(f"Accuracy:  {acc_svm:.4f} ({acc_svm*100:.2f}%)")
        print(f"Precision: {prec_svm:.4f} ({prec_svm*100:.2f}%)")
        results.append(("SVM", acc_svm, prec_svm))
        
        # 5. XGBoost
        print("\n5️⃣  XGBOOST")
        print("-" * 70)
        preds_xgb = xgb.predict(test[rolling_predictors])
        acc_xgb = accuracy_score(test["target"], preds_xgb)
        prec_xgb = precision_score(test["target"], preds_xgb)
        print(f"Accuracy:  {acc_xgb:.4f} ({acc_xgb*100:.2f}%)")
        print(f"Precision: {prec_xgb:.4f} ({prec_xgb*100:.2f}%)")
        results.append(("XGBoost", acc_xgb, prec_xgb))
        
        # Summary
        print("\n" + "="*70)
        print("📊 FINAL RANKING")
        print("="*70)
        
        results_df = pd.DataFrame(results, columns=['Model', 'Accuracy', 'Precision'])
        results_df = results_df.sort_values('Accuracy', ascending=False)
        results_df['Rank'] = range(1, len(results_df) + 1)
        
        print(results_df.to_string(index=False))
        
        # Best model details
        best_model = results_df.iloc[0]
        print("\n" + "="*70)
        print(f"🏆 WINNER: {best_model['Model']}")
        print("="*70)
        print(f"✅ Test Accuracy:  {best_model['Accuracy']:.4f} ({best_model['Accuracy']*100:.2f}%)")
        print(f"✅ Test Precision: {best_model['Precision']:.4f} ({best_model['Precision']*100:.2f}%)")
        
        # Sample predictions with best model
        print("\n" + "="*70)
        print("🔮 SAMPLE PREDICTIONS (Best Model)")
        print("="*70)
        
        combined = pd.DataFrame({
            'actual': test["target"], 
            'prediction': preds_rolling  # Using best model
        }, index=test.index)
        
        combined = combined.merge(
            matches_rolling[["date", "team", "opponent", "result"]], 
            left_index=True, 
            right_index=True
        )
        
        print("\nFirst 10 predictions:")
        print(combined[['team', 'opponent', 'result', 'actual', 'prediction']].head(10))
        
        # Accuracy breakdown
        correct = (combined['actual'] == combined['prediction']).sum()
        total = len(combined)
        print(f"\n✅ Correct predictions: {correct}/{total} ({correct/total*100:.2f}%)")
        
        # Feature importance (for best RF model)
        print("\n" + "="*70)
        print("📊 FEATURE IMPORTANCE (Random Forest + Rolling)")
        print("="*70)
        
        feature_imp = pd.DataFrame({
            'Feature': rolling_predictors,
            'Importance': rf_rolling.feature_importances_
        }).sort_values('Importance', ascending=False)
        
        print(feature_imp.head(10).to_string(index=False))
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        print("\nPlease run ML_models.ipynb first to train and save the models!")

else:
    print(f"\n❌ Models directory not found: {models_dir}")
    print("\n📝 To create models:")
    print("   1. Open ML_models.ipynb")
    print("   2. Run all cells")
    print("   3. Add the model saving cell at the end")
    print("   4. Run this script again")

print("\n" + "="*70)
print("Script completed!")
print("="*70)