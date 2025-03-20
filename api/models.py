import os
import json
import unicodedata
from pydantic import BaseModel
import asyncio
import random

this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")
stations_path = os.path.join(data_dir, "Estaciones_Troncales_de_TRANSMILENIO.geojson")
routes_path = os.path.join(data_dir, "Rutas_Troncales_de_TRANSMILENIO.geojson")


class Route(BaseModel):
    name: str = ""
    destination: str = ""


class Station(BaseModel):
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    arrivingRoutes: list[Route] = []


class Coords(BaseModel):
    latitude: float
    longitude: float


with open(stations_path, encoding="utf-8") as f:
    stations = json.load(f)

stations_dict = {}
for feature in stations["features"]:
    station_properties = feature["properties"]
    station_name = station_properties["nombre_estacion"]
    latitud = station_properties["latitud_estacion"]
    longitud = station_properties["longitud_estacion"]

    station_name = (
        unicodedata.normalize("NFKD", station_name)
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    stations_dict[station_name.replace(" ", "_").lower()] = Station(
        name=station_name, latitude=latitud, longitude=longitud
    )

del stations
print(stations_dict.keys())

with open(routes_path, encoding="utf-8") as f:
    routes = json.load(f)

routes_dict = {}
for feature in routes["features"]:
    route_properties = feature["properties"]
    # add route to routes_dict if it is operational
    if route_properties["estado_ruta_troncal"] == "OPERATIVA":
        route_name = route_properties["nombre_ruta_troncal"]

        # obtener nombre de la ruta como lo conoce el usuario
        route_name = route_name.split(" ")[0]
        route_destination = route_properties["destino_ruta_troncal"]
        route_destination = (
            unicodedata.normalize("NFKD", route_destination)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        routes_dict[f"{route_name} {route_destination}"] = Route(
            name=route_name, destination=route_destination
        )

del routes
print(routes_dict.values())


async def update_routes_locations():
    while True:
        for station in stations_dict.values():
            station.arrivingRoutes = random.sample(
                routes_dict.values(), k=random.randint(0, 2)
            )
        await asyncio.sleep(5)  # update every 5 secs
