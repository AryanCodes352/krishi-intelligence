import pandas as pd
import joblib
from ml.feature_engineering import build_features
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def evaluate():
    df = pd.read_csv('data/seed/wheat_lucknow_mandi.csv')
    df = build_features(df)
    test_df = df.iloc[-52:]
    
    model = joblib.load('ml/models/wheat_lucknow_xgb.joblib')
    features = ['month', 'day_of_year', 'year', 'week_of_year', 'lag_1w', 'lag_2w', 
                'lag_4w', 'lag_8w', 'rolling_mean_4w', 'rolling_mean_8w', 
                'rolling_std_4w', 'seasonal_index', 'msp_year', 'price_change_4w_pct']
    
    X_test = test_df[features]
    y_test = test_df['modal_price']
    
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mape = np.mean(np.abs((y_test - preds) / y_test)) * 100
    
    print("--- EVALUATION ---")
    print(f"MAE:  {mae:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"MAPE: {mape:.2f}%")
    
    importances = model.feature_importances_
    print("\nFeature Importances:")
    for f, imp in sorted(zip(features, importances), key=lambda x: x[1], reverse=True):
        print(f"{f}: {imp:.4f}")

if __name__ == "__main__":
    evaluate()
