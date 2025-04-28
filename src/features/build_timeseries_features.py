import pandas as pd
from pathlib import Path

def build_timeseries_features(input_file: str, output_dir: str):
    # Load processed crashes
    crashes = pd.read_csv(input_file, parse_dates=['crash_date'])

    # Aggregate citywide daily crash counts
    daily_city = (
        crashes
        .groupby('crash_date')
        .size()
        .reset_index(name='total_crashes')
        .sort_values('crash_date')
    )

    # Aggregate daily crash counts per neighborhood
    daily_neighborhood = (
        crashes
        .groupby(['crash_date', 'neighborhood'])
        .size()
        .reset_index(name='total_crashes')
        .sort_values(['neighborhood', 'crash_date'])
    )

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Save
    daily_city.to_parquet(Path(output_dir) / 'daily_city_crashes.parquet', index=False)
    daily_neighborhood.to_parquet(Path(output_dir) / 'daily_neighborhood_crashes.parquet', index=False)

if __name__ == "__main__":
    build_timeseries_features(
        input_file='../../data/processed/crashes.csv',
        output_dir='../../data/processed'
    )
