import pandas as pd
import numpy as np
import os
import json
import joblib
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from datetime import datetime, timezone
import warnings
from feature_engineering import build_features

warnings.filterwarnings('ignore')

def train():
    os.makedirs('ml/models', exist_ok=True)
    
    # Check if data exists
    data_path = 'data/seed/wheat_lucknow_mandi.csv'
    if not os.path.exists(data_path):
        print(f"Data file {data_path} not found. Creating dummy data for training.")
        os.makedirs('data/seed', exist_ok=True)
        dates = pd.date_range(start='2020-01-01', periods=350, freq='W')
        df = pd.DataFrame({
            'date': dates,
            'modal_price': np.random.normal(2000, 200, 350)
        })
        df.to_csv(data_path, index=False)
    
    df = pd.read_csv(data_path)
    df = build_features(df)
    
    train_df = df.iloc[:-52]
    test_df = df.iloc[-52:]
    
    features = ['month', 'day_of_year', 'year', 'week_of_year', 'lag_1w', 'lag_2w', 
                'lag_4w', 'lag_8w', 'rolling_mean_4w', 'rolling_mean_8w', 
                'rolling_std_4w', 'seasonal_index', 'msp_year', 'price_change_4w_pct']
                
    X_train = train_df[features]
    y_train = train_df['modal_price']
    X_test = test_df[features]
    y_test = test_df['modal_price']
    
    model = XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.05, subsample=0.8, random_state=42)
    model.fit(X_train, y_train)
    
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mape = np.mean(np.abs((y_test - preds) / y_test)) * 100
    
    print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}, MAPE: {mape:.2f}%")
    if mape > 15:
        print("WARNING: Model MAPE > 15%. Prediction confidence is LOW.")
        
    joblib.dump(model, 'ml/models/wheat_lucknow_xgb.joblib')
    
    meta = {
        "model_type": "XGBoost",
        "training_data_points": len(train_df),
        "test_data_points": len(test_df),
        "training_period": f"{train_df['date'].min().date()} to {train_df['date'].max().date()}",
        "mae": float(mae),
        "rmse": float(rmse),
        "mape_pct": float(mape),
        "features": features,
        "trained_at": datetime.now(timezone.utc).isoformat()
    }
    
    with open('ml/models/wheat_lucknow_meta.json', 'w') as f:
        json.dump(meta, f)
        
    print("Model trained and saved successfully.")

if __name__ == "__main__":
    train()
