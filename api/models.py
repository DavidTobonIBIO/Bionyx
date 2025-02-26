from pydantic import BaseModel
import asyncio
import random

STATION_NAMES = ["Universidades", "Aguas", "Portal 80", "Portal 170"]


class Bus(BaseModel):
    id: int
    route: str
    destination: str


class Station(BaseModel):
    name: str
    latitude: float = 0.0
    longitude: float = 0.0
    arrivingRoutes: list[Bus] = []


STATION_NAMES = ["Universidades", "Aguas", "Portal 80", "Portal 170"]
ROUTES = ["D24", "6", "8", "1", "B75", "B13"]
DESTINATIONS = [
    "Portal 80",
    "Portal 80",
    "Portal Norte",
    "Portal El Dorado",
    "Portal del Norte",
]

stations = {name.replace(" ", "_").lower(): Station(name=name) for name in STATION_NAMES}

buses = [
    Bus(id=i, route=route, destination=destination)
    for i, (route, destination) in enumerate(zip(ROUTES, DESTINATIONS))
]


async def update_bus_locations():
    while True:
        for station in stations.values():
            station.arrivingRoutes = random.sample(buses, k=random.randint(0, 2))
        await asyncio.sleep(5)  # update every 5 secs
