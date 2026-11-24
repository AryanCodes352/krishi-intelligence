import pandas as pd

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)
    df['month'] = df['date'].dt.month
    df['day_of_year'] = df['date'].dt.dayofyear
    df['year'] = df['date'].dt.year
    df['week_of_year'] = df['date'].dt.isocalendar().week
    
    df['lag_1w'] = df['modal_price'].shift(1)
    df['lag_2w'] = df['modal_price'].shift(2)
    df['lag_4w'] = df['modal_price'].shift(4)
    df['lag_8w'] = df['modal_price'].shift(8)
    
    df['rolling_mean_4w'] = df['modal_price'].shift(1).rolling(4).mean()
    df['rolling_mean_8w'] = df['modal_price'].shift(1).rolling(8).mean()
    df['rolling_std_4w'] = df['modal_price'].shift(1).rolling(4).std()
    
    overall_avg = df['modal_price'].mean()
    monthly_avg = df.groupby('month')['modal_price'].transform('mean')
    df['seasonal_index'] = monthly_avg / overall_avg
    
    df['msp_year'] = df['year'] # simplistic mapping
    df['price_change_4w_pct'] = (df['lag_1w'] - df['lag_4w']) / df['lag_4w'] * 100
    
    df = df.dropna().reset_index(drop=True)
    return df
