# NYC Vehicle Crashes Time Series Forecast & Dashboard

![image](https://github.com/user-attachments/assets/19684b2b-767f-492b-9d60-72bd7546466c)


This repository contains a full project pipeline for analyzing historical vehicle crashes in New York City, 
generating forecasts for future crashes, and visualizing results in an interactive dashboard. The dashboard allows users
to select a specific date range and neighborhood.

The dashboard allows users to:
- Explore historical crash data by neighborhood and time period.
- Forecast crash counts one year into the future using time series models.
- Visualize crash density on either a city-wide or neighborhood-specific basis using a plotly choropleth map.

---

## Project Structure

```
nyc-crashes-forecast/
├── app.py                         # Main Dash application
├── requirements.txt               # Required Python packages
├── README.md                      # Project documentation
├── data/
│   ├── external/
│   │   └── neighborhoods.geojson  # NYC neighborhood boundaries (geojson)
│   ├── processed/
│   │   ├── crashes.csv             # Cleaned and processed crash data
│   │   └── neighborhood_forecast_confidence.csv  # Forecast confidence levels
├── models/
│   └── crash_count_forecast/
│       └── sarima_model.pkl        # Pre-trained city-level SARIMA forecast model
├── notebooks/
│   ├── 01_preprocessing.ipynb      # Data cleaning and preprocessing
│   ├── 02_eda.ipynb                # Exploratory Data Analysis
│   ├── 03_model_forecast_total_crashes.ipynb   # City-wide forecasting
│   └── 04_model_forecast_per_neighborhood.ipynb # Neighborhood-level forecasts
├── reports/
│   └── figures/                    # Generated visualizations
├── src/
│   ├── data/                       # Data processing scripts
│   ├── features/                   # Feature engineering
│   ├── models/                     # Model training scripts
│   └── visualization/              # Visualization utilities
└── tox.ini                         # Testing configuration
```

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/zachpinto/nyc-crashes-ts-forecast.git
cd nyc-crashes-forecast
```

---

### 2. Set up a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate.bat  # Windows
```

---

### 3. Install requirements

```bash
pip install -r requirements.txt
```

---

### 4. Run the Dash app

```bash
python app.py
```

The app will be available at:

```
http://127.0.0.1:8050/
```

---

## Data Sources

- **Crash Data:** [NYC Open Data - Motor Vehicle Collisions](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data)
- **Neighborhood Boundaries:** [NYC Planning Open Data (GeoJSON format)](https://services5.arcgis.com/GfwWNkhOj9bNBqoJ/arcgis/rest/services/NYC_Neighborhood_Tabulation_Areas_2020/FeatureServer/0/query?where=1=1&outFields=*&outSR=4326&f=pgeojson)

---

## Model Details

- **SARIMAX Model:** Seasonal ARIMA used to forecast future crash counts based on historical daily crash volume.
- **Neighborhood Forecasts:** Neighborhood-level forecasts generated individually with their respective SARIMAX models.
- **Forecast Horizon:** 365 days ahead (one full year forecast).

---

## Features of the Dashboard

- **Forecast Toggle:** View either historical crash data or one-year forecast.
- **Date Range Selector:** Select custom date ranges.
- **Neighborhood Selector:** View data for specific NYC neighborhoods.
- **Infoboxes:** Display total crashes, injuries, and fatalities, either historically or projected.
- **Choropleth Map:** Visualize crash density geographically.
- **Time Series Plot:** View historical crash counts with a smoothed rolling average (to reduce noise).
- **Forecast Confidence Display:** View forecast confidence level for selected neighborhood.

---

## Deployment Notes

- The dashboard is designed to be **run locally** due to dataset size (~65 MB processed `.csv`).
- If hosting publicly (e.g., on a server or cloud), ensure large data files are available or host them separately and load dynamically.
- GitHub restricts pushing files over 100MB.
---

## Future Improvements

- Transition to a static, JavaScript-based visualization for public hosting without server dependencies.
- Integrate advanced forecasting models to account for time of day and weather conditions.
- Create automatic data refresh pipelines from NYC Open Data.

---

## License

This project is licensed under the MIT License.

---
