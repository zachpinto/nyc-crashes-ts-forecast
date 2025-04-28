import pandas as pd
import joblib
from pathlib import Path
from statsmodels.tsa.statespace.sarimax import SARIMAX

def main():
    # Load crash data
    daily_city = pd.read_parquet('../../data/processed/daily_city_crashes.parquet')
    daily_city['crash_date'] = pd.to_datetime(daily_city['crash_date'])
    daily_city = daily_city.set_index('crash_date')
    daily_city = daily_city.asfreq('D')

    # Train-test split (1 year holdout)
    train = daily_city.iloc[:-365]
    # test = daily_city.iloc[-365:]  # not used here, just training model

    # Fit SARIMA model
    model = SARIMAX(
        train['total_crashes'],
        order=(1,1,1),
        seasonal_order=(1,1,1,7),
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    sarima_result = model.fit(disp=False)

    # Save model
    Path('../../models/crash_count_forecast').mkdir(parents=True, exist_ok=True)
    joblib.dump(sarima_result, '../../models/crash_count_forecast/sarima_model.pkl')
    print("SARIMA model trained and saved to models/crash_count_forecast/sarima_model.pkl")

if __name__ == "__main__":
    main()
