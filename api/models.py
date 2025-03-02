import os
import json
import unicodedata
from pydantic import BaseModel
import asyncio
import random

this_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(this_dir)
data_dir = os.path.join(parent_dir, "data")
stations_path = os.path.join(data_dir, "tm_stations.geojson")

class Bus(BaseModel):
    id: int
    route: str
    destination: str


class Station(BaseModel):
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    arrivingRoutes: list[Bus] = []

class Coords(BaseModel):
    lat: float
    lon: float


with open(stations_path, encoding='utf-8') as f:
    stations = json.load(f)
    
stations_dict = {}
for feature in stations['features']:
    station_properties = feature['properties']
    station_name = station_properties['nombre_estacion']
    latitud = station_properties['latitud_estacion']
    longitud = station_properties['longitud_estacion']
    
    
    station_name = unicodedata.normalize('NFKD', station_name).encode('ascii', 'ignore').decode('ascii')
    station_name = station_name.replace(' ', '_').lower()
    
    stations_dict[station_name] = Station(name=station_name, latitude=latitud, longitude=longitud)
    

#print(stations_dict.keys())


ROUTES = ["D24", "6", "8", "1", "B75", "B13"]
DESTINATIONS = [
    "Portal 80",
    "Portal 80",
    "Portal Norte",
    "Portal El Dorado",
    "Portal Norte",
]

buses = [
    Bus(id=i, route=route, destination=destination)
    for i, (route, destination) in enumerate(zip(ROUTES, DESTINATIONS))
]


async def update_bus_locations():
    while True:
        for station in stations_dict.values():
            station.arrivingRoutes = random.sample(buses, k=random.randint(0, 2))
        await asyncio.sleep(5)  # update every 5 secs
