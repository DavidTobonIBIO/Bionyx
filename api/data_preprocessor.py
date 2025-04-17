import os 
import json
from os.path import join as path_join
import pandas as pd

from utils import load_text_file

# Paths
this_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = path_join(this_dir, 'data')

# GTFS files
GTFS_dir = path_join(data_dir, 'GTFS_TM_2023')

routes_GTFS = path_join(GTFS_dir, 'routes.txt')
stop_times_GTFS = path_join(GTFS_dir, 'stop_times.txt')
trips_GTFS = path_join(GTFS_dir, 'trips.txt')
stops_GTFS = path_join(GTFS_dir, 'stops.txt')

# GeoJSON file
routes_geojson = path_join(data_dir, 'Rutas_Troncales_de_TRANSMILENIO.geojson')

# Load GeoJSON data
with open(routes_geojson, 'r', encoding='utf-8') as f:
    routes_gj_data = json.load(f)

routes_features_lt = routes_gj_data['features']
print(f"Total routes in geojson: {len(routes_features_lt)}")

# Load GTFS data
routes_gtfs_data = load_text_file(routes_GTFS)
stop_times_gtfs_data = load_text_file(stop_times_GTFS)
trips_gtfs_data = load_text_file(trips_GTFS)
stops_gtfs_data = load_text_file(stops_GTFS)

# Match GTFS routes with GeoJSON route names
matched_routes_lt = []
for route_gtfs in routes_gtfs_data.iterrows():
    route_name_gtfs = route_gtfs[1]['route_short_name']
    
    for route_geojson in routes_features_lt:
        route_properties = route_geojson['properties']
        route_name_geojson = route_properties['route_name_ruta_troncal']
        servicio_troncal = route_properties['servicio_unico_ruta_troncal']
        
        
        if (route_name_gtfs == route_name_geojson) or (route_name_gtfs == servicio_troncal): #FIXME 
            
            matched_routes_lt.append(route_name_gtfs)

print(f"Matched routes: {len(matched_routes_lt)}")

# Filter only TRONCAL routes
final_routes_df = pd.DataFrame()
for filtered_route in matched_routes_lt:
    for route_gtfs in routes_gtfs_data.iterrows():
        route_name_gtfs = route_gtfs[1]['route_short_name']
        route_desc = route_gtfs[1]['route_desc']

        if (filtered_route == route_name_gtfs) and (route_desc == 'TRONCAL'):
            final_routes_df = pd.concat([final_routes_df, route_gtfs[1].to_frame().T], ignore_index=True)

print(f"Final TRONCAL routes: {len(final_routes_df)}")
print(final_routes_df.head())

# Collect stops per route
final_stop_times_df = pd.DataFrame()
route_stop_mapping = {}

for filtered_route in final_routes_df.iterrows():
    route_name_gtfs = filtered_route[1]['route_short_name']
    route_id = filtered_route[1]['route_id']
    print(f"\nProcessing route: {route_name_gtfs}")

    route_trips = trips_gtfs_data[trips_gtfs_data['route_id'] == route_id]
    route_trip_ids = route_trips['trip_id'].unique()

    if len(route_trip_ids) == 0:
        print(f"No trips found for route {route_name_gtfs}")
        continue

    route_stop_times = stop_times_gtfs_data[stop_times_gtfs_data['trip_id'].isin(route_trip_ids)]
    route_stop_ids = route_stop_times['stop_id'].drop_duplicates()

    if len(route_stop_ids) == 0:
        print(f"No stops found for route {route_name_gtfs}")
        continue

    route_stops = stops_gtfs_data[stops_gtfs_data['stop_id'].isin(route_stop_ids)].copy()
    route_stops['route_short_name'] = route_name_gtfs

    final_stop_times_df = pd.concat([final_stop_times_df, route_stops], ignore_index=True)

    stop_names = sorted(route_stops['stop_name'].unique().tolist())
    route_stop_mapping[route_name_gtfs] = stop_names

# Print summary
print(f"\nTotal unique stops collected: {len(final_stop_times_df['stop_id'].unique())}")
print(final_stop_times_df[['stop_id', 'stop_name', 'route_short_name']].head())

# Optional: print example route mapping
sample_route = list(route_stop_mapping.keys())[0]
print(f"\nExample: Route {sample_route} has {len(route_stop_mapping[sample_route])} stops:")
print(route_stop_mapping[sample_route])

# Optional: export to CSV
output_path = path_join(data_dir, 'route_stop_mapping.csv')
final_stop_times_df.to_csv(output_path, index=False)
print(f"\nSaved full stop list to: {output_path}")
