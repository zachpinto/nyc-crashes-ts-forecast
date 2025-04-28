import json
import pandas as pd
import plotly.express as px

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import joblib
from statsmodels.tsa.statespace.sarimax import SARIMAX

# ─── Data loading ──────────────────────────────────────────────────────────────

crashes = pd.read_csv(
    'data/processed/crashes.csv',
    parse_dates=['crash_date']
)
crashes.rename(columns={
    'number_of_persons_killed': 'killed',
    'number_of_persons_injured': 'injured'
}, inplace=True)

confidence = pd.read_csv('data/processed/neighborhood_forecast_confidence.csv')

with open('data/external/neighborhoods.geojson') as f:
    geojson_nbhd = json.load(f)

# Load the city SARIMA model
city_model = joblib.load('models/crash_count_forecast/sarima_model.pkl')


# ─── Dash app setup ────────────────────────────────────────────────────────────

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.title = "NYC Motor Vehicle Crashes Dashboard"


# ─── Layout ────────────────────────────────────────────────────────────────────

app.layout = dbc.Container(fluid=True, children=[

    # Top row: Parameters | Info cards
    dbc.Row([

        # ─── Parameters (Left) ────────────────────────────────────────────────────
        dbc.Col(
            dbc.Card([
                dbc.CardBody([

                    # Placeholder title + about icon
                    html.Div([
                        html.H5("NYC Vehicle Collisions Time Series", className="text-white d-inline mb-3"),
                        html.Span(
                            "ℹ️",
                            id="about-icon",
                            style={"cursor":"pointer","marginLeft":"0.5rem","color":"#FFFFFF"}
                        )
                    ], className="mb-3"),

                    # Popover shown when info icon is clicked
                    # replace your existing PopoverBody with this:
                    dbc.Popover(
                        [
                            dbc.PopoverHeader(
                                "About",
                                style={'fontFamily': 'Arial, sans-serif', 'fontSize': '1.1em', 'color': 'black'}
                            ),
                            dbc.PopoverBody(
                                html.Div([
                                    html.P(
                                        "This dashboard is an interactive tool that gives an historical analysis and "
                                        "forecast of vehicle collisions for both city-wide and "
                                        "neighborhood-specific bases.",
                                        style={'fontFamily': 'Arial, sans-serif', 'fontSize': '0.9em', 'color': 'white',
                                               'marginBottom': '0.5rem'}
                                    ),
                                    html.P("NOTE: The 'Forecast' option only shows totals for the period of a one-year forecast"),
                                    html.A(
                                        "Learn more here",
                                        href="https://github.com/zachpinto/nyc-crashes",
                                        # replace with your link
                                        target="_blank",
                                        style={'color': '#636EFB', 'textDecoration': 'underline', 'fontSize': '0.85em'}
                                    )
                                ]),
                                style={'backgroundColor': '#252e3f'}
                            )
                        ],
                        target="about-icon",
                        trigger="click",
                        placement="right"
                    ),


                    # Actual controls
                    dbc.Row([

                        # Data Type radios
                        dbc.Col([
                            html.Label(
                                "Historical or Forecast:",
                                className="text-white mb-1 mt-n1",
                                style={'fontSize':'1.05em'}
                            ),

                            dcc.RadioItems(
                                id='data_type',
                                options=[
                                    {'label': 'Historical', 'value': 'historical'},
                                    {'label': 'Forecast',   'value': 'forecast'}
                                ],
                                value='historical',
                                inline=True,
                                labelStyle={'color':'white','fontSize':'1.1em','marginRight':'1.5rem'},
                                inputStyle={'marginRight':'0.5rem'}
                            )
                        ], width=4,
                           className="d-flex flex-column justify-content-center",
                           style={'fontSize':'1.05em'}),

                        # Date range + neighborhood selector
                        dbc.Col([

                            html.Div([
                                html.Label("Date Range:", className="text-white mb-1"),
                                dcc.DatePickerRange(
                                    id='date_picker',
                                    min_date_allowed=crashes['crash_date'].min(),
                                    max_date_allowed=crashes['crash_date'].max(),
                                    start_date=crashes['crash_date'].min(),
                                    end_date=crashes['crash_date'].max(),
                                    display_format='YYYY-MM-DD',
                                    style={'width':'100%','fontSize':'1.05em'}
                                )
                            ], className="mb-4"),

                            html.Div([
                                html.Label("Select Neighborhood:", className="text-white mb-1"),
                                dcc.Dropdown(
                                    id='neighborhood_selector',
                                    options=[{'label': n, 'value': n}
                                             for n in sorted(crashes['neighborhood'].dropna().unique())],
                                    placeholder="All Neighborhoods",
                                    clearable=True,
                                    style={
                                        'width':'100%',
                                        'fontSize':'1.05em',
                                        'color':'black',
                                        'backgroundColor':'white'
                                    }
                                ),
                                # 2) show confidence level underneath
                                html.Div(id='neighborhood_confidence', className="text-white mt-2")
                            ])

                        ], width=8,
                           className="d-flex flex-column justify-content-center"),

                    ], className="h-100")

                ], style={'color':'white'})
            ], color='#252e3f', inverse=True, style={'height':'300px'}),  # moved down, made taller
        width=6),


        # Info cards (Right)
        dbc.Col(
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Crashes", className="card-title text-center"),
                        html.H4(
                            id='total_crashes',
                            className="text-center",
                            style={'color':'#636EFB','fontSize':'2rem','marginTop':'5rem'}
                        )
                    ])
                ], color='#252e3f', inverse=True, style={'height':'300px'}), width=4),

                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Injured", className="card-title text-center"),
                        html.H4(
                            id='total_injured',
                            className="text-center",
                            style={'color':'#636EFB','fontSize':'2rem','marginTop':'5rem'}
                        )
                    ])
                ], color='#252e3f', inverse=True, style={'height':'300px'}), width=4),

                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.H6("Total Killed", className="card-title text-center"),
                        html.H4(
                            id='total_killed',
                            className="text-center",
                            style={'color':'#636EFB','fontSize':'2rem','marginTop':'5rem'}
                        )
                    ])
                ], color='#252e3f', inverse=True, style={'height':'300px'}), width=4),
            ], className="g-3"),
        width=6),
    ], className="mt-4 mb-4"),


    html.Hr(className="border-secondary"),


    # Bottom row: Map | Time series
    dbc.Row([

        # Map panel
        dbc.Col([
            dcc.Graph(
                id='crash_map',
                config={'displayModeBar': False},
                style={'height':'425px'}
            ),
        ], width=6),


        # Time series panel
        dbc.Col([
            dcc.Graph(
                id='time_series_chart',
                config={'displayModeBar': False},
                style={'height':'425px','backgroundColor':'#252e3f'}
            ),
        ], width=6),

    ]),

])


# ─── Callbacks ─────────────────────────────────────────────────────────────────

# 1) Infoboxes: handle Historical vs Forecast
@app.callback(
    [
        Output('total_crashes','children'),
        Output('total_killed','children'),
        Output('total_injured','children'),
    ],
    [
        Input('date_picker','start_date'),
        Input('date_picker','end_date'),
        Input('neighborhood_selector','value'),
        Input('data_type','value'),
    ]
)
def update_infoboxes(start_date,end_date,neighborhood,data_type):
    sd = pd.to_datetime(start_date).date()
    ed = pd.to_datetime(end_date).date()
    min_d = crashes['crash_date'].min().date()
    max_d = crashes['crash_date'].max().date()

    # Historical + full range + no neighborhood
    if data_type=='historical' and sd==min_d and ed==max_d and not neighborhood:
        return "2,171,175","3,367","699,348"

    # Historical + any filter
    if data_type=='historical':
        dff = crashes[(crashes['crash_date'].dt.date>=sd)&(crashes['crash_date'].dt.date<=ed)]
        if neighborhood:
            dff = dff[dff['neighborhood']==neighborhood]
        return f"{len(dff):,}",f"{int(dff['killed'].sum()):,}",f"{int(dff['injured'].sum()):,}"

    # Forecast mode
    if neighborhood:
        df_nb = crashes[crashes['neighborhood']==neighborhood]
        ratio_i = df_nb['injured'].sum()/len(df_nb) if len(df_nb)>0 else 0
        ratio_k = df_nb['killed'].sum()/len(df_nb)  if len(df_nb)>0 else 0
        ts = df_nb.groupby('crash_date').size().asfreq('D').fillna(0)
        model = SARIMAX(ts,order=(1,1,1),seasonal_order=(1,1,1,7),
                        enforce_stationarity=False,enforce_invertibility=False).fit(disp=False)
        fc = model.get_forecast(365).predicted_mean
    else:
        fc = city_model.get_forecast(365).predicted_mean
        ratio_i = crashes['injured'].sum()/len(crashes)
        ratio_k = crashes['killed'].sum()/len(crashes)

    total_fc = fc.sum()
    injured_fc = int(round(total_fc*ratio_i))
    killed_fc  = int(round(total_fc*ratio_k))
    return f"{int(round(total_fc)):,}",f"{killed_fc:,}",f"{injured_fc:,}"


# 2) Map callback with bounds zoom
@app.callback(
    Output('crash_map','figure'),
    [
        Input('date_picker','start_date'),
        Input('date_picker','end_date'),
        Input('neighborhood_selector','value'),
    ]
)
def update_map(start_date,end_date,neighborhood):
    dff = crashes[(crashes['crash_date']>=start_date)&(crashes['crash_date']<=end_date)]
    if neighborhood:
        dff = dff[dff['neighborhood']==neighborhood]

    agg = dff.groupby('neighborhood').size().reset_index(name='value')
    all_nb = pd.DataFrame({'neighborhood':confidence['neighborhood']})
    agg = all_nb.merge(agg,on='neighborhood',how='left').fillna(0)

    fig = px.choropleth_mapbox(
        agg, geojson=geojson_nbhd,
        locations='neighborhood', featureidkey='properties.NTAName',
        color='value', hover_data=['value'],
        mapbox_style='carto-darkmatter',
        opacity=0.7, color_continuous_scale='OrRd'
    )
    fig.update_layout(
        coloraxis_showscale=False,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)'
    )

    if neighborhood:
        feat = next(f for f in geojson_nbhd['features']
                    if f['properties']['NTAName']==neighborhood)
        pts = []
        def _extract(c):
            if isinstance(c[0],(list,tuple)) and not isinstance(c[0][0],(float,int)):
                for part in c: _extract(part)
            else:
                for lon,lat in c: pts.append((lon,lat))

        geom = feat['geometry']
        coords = geom['coordinates']
        if geom['type']=="Polygon":
            _extract(coords)
        else:
            for poly in coords: _extract(poly)

        lons,lats = zip(*pts)
        bbox = {'west':min(lons),'south':min(lats),
                'east':max(lons),'north':max(lats)}
        fig.update_layout(mapbox=dict(bounds=bbox))
    else:
        fig.update_layout(mapbox=dict(center={"lat":40.7128,"lon":-74.0060},zoom=9))

    return fig


# 3) Time series + 7-day rolling + forecast overlay
@app.callback(
    Output('time_series_chart','figure'),
    [
        Input('date_picker','start_date'),
        Input('date_picker','end_date'),
        Input('neighborhood_selector','value'),
        Input('data_type','value'),
    ]
)
def update_time_series(start_date,end_date,neighborhood,data_type):
    dff = crashes[(crashes['crash_date']>=start_date)&(crashes['crash_date']<=end_date)]
    if neighborhood:
        dff = dff[dff['neighborhood']==neighborhood]

    daily = dff.groupby('crash_date').size().rename('value')
    daily = daily.asfreq('D',fill_value=0)
    smoothed = daily.rolling(window=7,center=True,min_periods=1).mean()
    hist = smoothed.reset_index()

    fig = px.line(hist,x='crash_date',y='value',
                  labels={'crash_date':'Date','value':'Crashes'},
                  template='plotly_dark')

    if data_type=='forecast':
        last = hist['crash_date'].max()
        future = pd.date_range(last+pd.Timedelta(days=1),periods=365,freq='D')
        if neighborhood:
            df_nb = crashes[crashes['neighborhood']==neighborhood]
            ts = df_nb.groupby('crash_date').size().asfreq('D').fillna(0)
            model = SARIMAX(ts,order=(1,1,1),seasonal_order=(1,1,1,7),
                            enforce_stationarity=False,enforce_invertibility=False).fit(disp=False)
            vals = model.get_forecast(365).predicted_mean.values
        else:
            vals = city_model.get_forecast(365).predicted_mean.values

        fc_df = pd.DataFrame({'crash_date':future,'value':vals})
        fc_df['smoothed'] = fc_df['value'].rolling(window=7, center=True, min_periods=1).mean()

        fig.add_scatter(
            x=fc_df['crash_date'],
            y=fc_df['smoothed'],
            mode='lines',
            line=dict(shape='spline', color='orange'),  # spline makes it smoother
            name='Forecast (7d MA)'
        )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')
    return fig


# 4) Auto-set start-date when Forecast selected
@app.callback(
    Output('date_picker','start_date'),
    Input('data_type','value')
)
def _auto_set_start(data_type):
    if data_type=='forecast':
        return '2021-04-22'
    return crashes['crash_date'].min().date().isoformat()


# 5) Neighborhood confidence display
@app.callback(
    Output('neighborhood_confidence','children'),
    Input('neighborhood_selector','value')
)
def update_confidence(neighborhood):
    if neighborhood:
        lvl = confidence.loc[confidence['neighborhood']==neighborhood,'confidence_level'].iloc[0]
        return f"Forecast: {lvl}"
    return ""


# ─── Run server ────────────────────────────────────────────────────────────────

if __name__=='__main__':
    app.run(debug=True)
