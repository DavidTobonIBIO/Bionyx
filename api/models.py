import os
import json
import unicodedata
from pydantic import BaseModel
import asyncio
import random


class Coords(BaseModel):
    latitude: float
    longitude: float


class Station(BaseModel):
    id: int
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    arrivingRoutes: list["Route"] = []


class Route(BaseModel):
    id: int
    name: str
    destinationStationId: int


this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")
stations_path = os.path.join(data_dir, "Estaciones_Troncales_de_TRANSMILENIO.geojson")
routes_path = os.path.join(data_dir, "Rutas_Troncales_de_TRANSMILENIO.geojson")

with open(stations_path, encoding="utf-8") as f:
    stations = json.load(f)

stations_dict_by_names = {}
stations_dict = {}
for feature in stations["features"]:
    station_properties = feature["properties"]
    id = station_properties["objectid"]
    station_name = station_properties["nombre_estacion"]
    latitud = station_properties["latitud_estacion"]
    longitud = station_properties["longitud_estacion"]
    station_name = (
        unicodedata.normalize("NFKD", station_name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    
    station = Station(id=id, name=station_name, latitude=latitud, longitude=longitud)
    stations_dict_by_names[station_name.replace(" ", "_").lower()] = station
    stations_dict[id] = station

del stations

with open(routes_path, encoding="utf-8") as f:
    routes = json.load(f)

routes_dict = {}
for feature in routes["features"]:
    route_properties = feature["properties"]
    # add route to routes_dict if it is operational
    if route_properties["estado_ruta_troncal"] == "OPERATIVA":
        id = route_properties["objectid"]
        route_name = route_properties["nombre_ruta_troncal"]

        # obtener nombre de la ruta como lo conoce el usuario
        route_name = route_name.split(" ")[0]
        route_destination_name = route_properties["destino_ruta_troncal"]
        route_destination_name = (
            unicodedata.normalize("NFKD", route_destination_name)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        destination_name_key = route_destination_name.replace(" ", "_").lower()

        routeDestinationStation = stations_dict_by_names.get(destination_name_key, None)

        if not routeDestinationStation:
            print(
                f"Destination station {route_destination_name} not found for route {route_name}"
            )
            continue

        routes_dict[id] = Route(
            id=id, name=route_name, destinationStationId=routeDestinationStation.id
        )

del routes

routes_list = sorted(list(routes_dict.values()), key=lambda route: route.name)


async def update_routes_locations():
    while True:
        for station in stations_dict_by_names.values():
            station.arrivingRoutes = station.arrivingRoutes = [
                Route(id=r.id, name=r.name, destination=r.destination)
                for r in random.sample(routes_list, k=random.randint(0, 4))
            ]
        await asyncio.sleep(5)  # update every 5 secs
