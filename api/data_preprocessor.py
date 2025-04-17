import os 
import json
from os.path import join as path_join
import pandas as pd

this_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = path_join(this_dir, 'data')

GTFS_dir = path_join(data_dir, 'GTFS_TM_2023')

routes_GTFS = path_join(GTFS_dir, 'routes.txt')

routes_geojson = path_join(data_dir, 'Rutas_Troncales_de_TRANSMILENIO.geojson')

with open(routes_geojson, 'r', encoding='utf-8') as f:
    routes_gj_data = json.load(f)
    
with open(routes_GTFS, 'r', encoding='utf-8') as f:
    routes_gtfs_data = pd.read_csv(f, encoding='utf-8')

routes_features_lt = routes_gj_data['features']
print(f"Total routes in geojson: {len(routes_features_lt)}")

matched_routes_lt = []
    
counter = 0
for route_gtfs in routes_gtfs_data.iterrows():
    route_name_gtfs = route_gtfs[1]['route_short_name']
    
    for route_geojson in routes_features_lt:
        route_properties = route_geojson['properties']
        route_name_geojson = route_properties['route_name_ruta_troncal']
        
        if route_name_gtfs == route_name_geojson:
        
            matched_routes_lt.append(route_name_gtfs)

print(f"Matched routes: {len(matched_routes_lt)}")

final_routes_df = pd.DataFrame()

for filtered_route in matched_routes_lt:
    for route_gtfs in routes_gtfs_data.iterrows():
        route_name_gtfs = route_gtfs[1]['route_short_name']
        route_desc = route_gtfs[1]['route_desc']

        if (filtered_route == route_name_gtfs) and (route_desc == 'TRONCAL'):
            final_routes_df = pd.concat([final_routes_df, route_gtfs[1].to_frame().T], ignore_index=True)

print(f"Final routes: {len(final_routes_df)}")
print(final_routes_df.head())
