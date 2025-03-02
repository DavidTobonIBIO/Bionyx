import os
import json
import unicodedata

this_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(this_dir)
data_dir = os.path.join(parent_dir, "data")
stations_path = os.path.join(data_dir, "tm_stations.geojson")

with open(stations_path, encoding='utf-8') as f:
    stations = json.load(f)
    
new_station_dict = {}
for feature in stations['features']:
    station_properties = feature['properties']
    station_name = station_properties['nombre_estacion']
    latitud = station_properties['latitud_estacion']
    longitud = station_properties['longitud_estacion']
    
    
    station_name = unicodedata.normalize('NFKD', station_name).encode('ascii', 'ignore').decode('ascii')
    station_name = station_name.replace(' ', '_').lower()
    
    new_station_dict[station_name] = {
        "name": station_name,
        "lat": latitud,
        "lon": longitud
    }
    
    
print(new_station_dict)  # {'Bishan': {'name': 'Bishan', 'lat': 1.2894, 'lon': 103.8404}, 'Braddell': {'name': 'Braddell', 'lat': 1.3404, 'lon': 103.8463}, 'Caldecott': {'name': 'Caldecott', 'lat': 1.3374, 'lon': 103.8394}, 'Toa Payoh': {'name': 'Toa Payoh', 'lat': 1.3324, 'lon': 103.8474}, 'Novena': {'name': 'Novena', 'lat': 1.3204, 'lon': 103.8434}, 'Newton': {'name': 'Newton', 'lat': 1.3124, 'lon': 103.8394}, 'Orchard': {'name': 'Orchard', 'lat': 1.3034, 'lon': 103.8324}, 'Somerset': {'name': 'Somerset', 'lat': 1.3004, 'lon': 103.8384}, 'Dhoby Ghaut': {'name': 'Dhoby Ghaut', 'lat': 1.2984, 'lon': 103.8464}, 'City Hall': {'name': 'City Hall', 'lat': 1.2934, 'lon': 103.8524}, 'Raffles Place': {'name': 'Raffles Place', 'lat': 1.2834, 'lon': 103.8514}, 'Marina Bay': {'name': 'Marina Bay', 'lat': 1.2764, 'lon': 103.8544}, 'Marina South Pier': {'name': 'Marina South Pier', 'lat': 1.2714, 'lon': 103.8624}}
