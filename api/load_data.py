import os
import json
import unicodedata
from models import Coordinates, Route, Station
from shapely.geometry import Point, shape

this_dir: str = os.path.dirname(__file__)
data_dir: str = os.path.join(this_dir, "data")
stations_path: str = os.path.join(
    data_dir, "Estaciones_Troncales_de_TRANSMILENIO.geojson"
)
routes_path: str = os.path.join(data_dir, "Rutas_Troncales_de_TRANSMILENIO.geojson")


def load_stations() -> tuple[dict[int, Station], dict[str, Station]]:
    with open(stations_path, encoding="utf-8") as f:
        stations_geojson = json.load(f)

    stations_dict_by_names: dict[str, Station] = {}
    stations_dict: dict[int, Station] = {}
    for feature in stations_geojson["features"]:
        station_properties = feature["properties"]
        id: int = station_properties["objectid"]
        station_name: str = station_properties["nombre_estacion"].upper()
        latitud: float = station_properties["latitud_estacion"]
        longitud: float = station_properties["longitud_estacion"]
        station_name = (
            unicodedata.normalize("NFKD", station_name)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        coordinates: Coordinates = Coordinates(latitude=latitud, longitude=longitud)
        station: Station = Station(id=id, name=station_name, coordinates=coordinates)
        stations_dict_by_names[station_name.replace(" ", "_").lower()] = station
        stations_dict[id] = station

    del stations_geojson

    return stations_dict, stations_dict_by_names


def load_routes(
    stations_dict_by_names: dict[str, Station],
) -> tuple[dict[int, Route], list[Route]]:
    with open(routes_path, encoding="utf-8") as f:
        routes_geojson = json.load(f)

    routes_dict: dict[int, Route] = {}
    for feature in routes_geojson["features"]:
        route_properties = feature["properties"]
        # add route to routes_dict if it is operational
        if route_properties["estado_ruta_troncal"] == "OPERATIVA":
            id: int = route_properties["objectid"]
            route_name: str = route_properties["nombre_ruta_troncal"]

            # obtener nombre de la ruta como lo conoce el usuario
            route_name = route_name.split(" ")[0]
            route_destination_name: str = route_properties["destino_ruta_troncal"]
            route_destination_name = (
                unicodedata.normalize("NFKD", route_destination_name)
                .encode("ascii", "ignore")
                .decode("ascii")
            )
            destination_name_key: str = route_destination_name.replace(" ", "_").lower()

            routeDestinationStation: Station = stations_dict_by_names.get(
                destination_name_key, None
            )

            if not routeDestinationStation:
                print(
                    f"Destination station {route_destination_name} not found for route {route_name}"
                )
                continue

            route_origin_name: str = route_properties["origen_ruta_troncal"]
            route_origin_name = (
                unicodedata.normalize("NFKD", route_origin_name)
                .encode("ascii", "ignore")
                .decode("ascii")
            )
            origin_name_key: str = route_origin_name.replace(" ", "_").lower()

            routeOriginStation: Station = stations_dict_by_names.get(
                origin_name_key, None
            )
            if not routeOriginStation:
                print(
                    f"Origin station {route_origin_name} not found for route {route_name}"
                )
                continue

            routes_dict[id] = Route(
                id=id,
                name=route_name,
                destinationStationId=routeDestinationStation.id,
                originStationId=routeOriginStation.id,
            )

    del routes_geojson

    routes_list: list[Route] = sorted(
        list(routes_dict.values()), key=lambda route: route.name
    )

    return routes_dict, routes_list


def set_arriving_routes(
    stations_dict: dict[int, Station], routes_dict: dict[int, Route]
) -> None:
    with open(routes_path, encoding="utf-8") as f:
        routes_geojson = json.load(f)

    for station in stations_dict.values():
        station_point = Point(
            station.coordinates.longitude, station.coordinates.latitude
        )

        arriving_routes = []
        for feature in routes_geojson["features"]:
            geometry = shape(feature["geometry"])
            distance = geometry.distance(station_point)

            if (
                distance < 0.001
                and feature["properties"]["estado_ruta_troncal"] == "OPERATIVA"
            ):
                route_id = feature["properties"]["objectid"]
                route = routes_dict.get(route_id, None)
                if not route:
                    continue
                destination_station: Station = stations_dict.get(
                    route.destinationStationId, None
                )
                origin_station: Station = stations_dict.get(route.originStationId, None)

                if destination_station:
                    if destination_station.id == origin_station.id:
                        arriving_routes.append(route)
                    elif destination_station.id != station.id:
                        arriving_routes.append(route)

        station.arrivingRoutes = arriving_routes


def load_data() -> (
    tuple[dict[int, Station], dict[str, Station], dict[int, Route], list[Route]]
):
    print("Loading data...")
    stations_dict, stations_dict_by_names = load_stations()
    routes_dict, routes_list = load_routes(stations_dict_by_names)

    print("Setting arriving routes...")
    set_arriving_routes(stations_dict, routes_dict)

    print("Loaded data.")
    return stations_dict, stations_dict_by_names, routes_dict, routes_list
