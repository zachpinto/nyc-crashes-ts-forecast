import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from tqdm import tqdm

def main():
    # Load neighborhood-level crash counts
    daily_nbhd = pd.read_parquet('../../data/processed/daily_neighborhood_crashes.parquet')

    # Ensure datetime and sorted
    daily_nbhd['crash_date'] = pd.to_datetime(daily_nbhd['crash_date'])
    daily_nbhd = daily_nbhd.sort_values(['neighborhood', 'crash_date'])

    neighborhoods = daily_nbhd['neighborhood'].unique()

    results = []  # to store evaluation metrics

    for nbhd in tqdm(neighborhoods, desc="Training SARIMA models"):
        nbhd_df = daily_nbhd[daily_nbhd['neighborhood'] == nbhd]

        # Pivot to time series (daily frequency)
        ts = nbhd_df.set_index('crash_date')['total_crashes'].asfreq('D').fillna(0)

        # Skip neighborhoods with too little data
        if len(ts) < 400:
            continue

        # Skip neighborhoods that are too empty (low activity)
        if ts.mean() < 0.5:
            continue

        # Train-test split
        train = ts.iloc[:-365]
        test = ts.iloc[-365:]

        # Fit SARIMA
        try:
            model = SARIMAX(
                train,
                order=(1,1,1),
                seasonal_order=(1,1,1,7),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            result = model.fit(disp=False)

            # Forecast
            forecast = result.get_forecast(steps=len(test))
            forecast_mean = forecast.predicted_mean

            # Evaluate
            mae = (abs(forecast_mean - test)).mean()
            rmse = ((forecast_mean - test) ** 2).mean() ** 0.5

            results.append({
                'neighborhood': nbhd,
                'mae': mae,
                'rmse': rmse
            })

        except Exception as e:
            print(f"Failed on {nbhd}: {e}")

    # Save results
    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv('../../reports/metrics/neighborhood_forecast_metrics.csv', index=False)

    print("Finished training and evaluation. Metrics saved to reports/metrics/neighborhood_forecast_metrics.csv.")

if __name__ == "__main__":
    main()
