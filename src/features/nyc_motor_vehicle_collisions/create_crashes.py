import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

crashes = pd.read_csv('../../../data/interim/crashes.csv')
neighborhoods = gpd.read_file('../../../data/external/neighborhoods.geojson')

crashes_gdf = gpd.GeoDataFrame(
    crashes,
    geometry=gpd.points_from_xy(crashes.longitude, crashes.latitude),
    crs='EPSG:4326'
)

crashes_with_neighborhood = gpd.sjoin(
    crashes_gdf, neighborhoods[['NTAName', 'geometry']],
    how='left',
    predicate='within'
)

# Drop crashes with no matched neighborhood
crashes_with_neighborhood = crashes_with_neighborhood.dropna(subset=['NTAName'])

# Drop spatial columns and rename
crashes_with_neighborhood = crashes_with_neighborhood.drop(columns=['geometry', 'index_right'])
crashes_with_neighborhood = crashes_with_neighborhood.rename(columns={'NTAName': 'neighborhood'})

crashes_with_neighborhood.to_csv('../../data/processed/crashes.csv', index=False)
