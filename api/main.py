from fastapi import FastAPI, HTTPException
from models import Coords, Route, Station, update_routes_locations, stations_dict, routes_dict, routes_list
import asyncio
from contextlib import asynccontextmanager
import uvicorn
import math
import os
import shutil
import atexit


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up and launching background tasks...")
    task = asyncio.create_task(update_routes_locations())
    yield
    task.cancel()
    print("Shutting down.")


app = FastAPI(root_path="/api", lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "OrientApp Backend"}


@app.get("/routes/", response_model=list[Route])
async def read_routes_names():
    return routes_list


@app.get("/routes/{id}", response_model=Route)
async def read_route(id: int):
    route = routes_dict.get(id)
    if route:
        return route
    else:
        raise HTTPException(status_code=404, detail=f"Route with id={id} not found")


@app.get("/stations/", response_model=list[Station])
async def read_stations():
    return list(stations_dict.values())


@app.get("/stations/{name}", response_model=Station)
async def read_station(name: str):
    if name not in stations_dict:
        raise HTTPException(status_code=404, detail=f"Station {name} not found")
    return stations_dict[name]


@app.post("/stations/nearest_station", response_model=Station)
async def read_nearest_station(coords: Coords):
    nearest_station = None
    R = 6371000  # Radius of Earth in m
    nearest_distance = math.inf  # Nearest distance in m

    lat1, lon1 = coords.latitude, coords.longitude

    for station in stations_dict.values():

        lat2, lon2 = station.latitude, station.longitude
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) * math.sin(dphi / 2) + math.cos(phi1) * math.cos(
            phi2
        ) * math.sin(dlambda / 2) * math.sin(dlambda / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c  # Distance in m

        if distance < nearest_distance:
            nearest_station = station
            nearest_distance = distance

    if nearest_station is None:
        raise HTTPException(status_code=404, detail=f"No stations found")

    return nearest_station


def remove_pycache():
    pycache_path = os.path.join(this_script_dir, "__pycache__")
    if os.path.exists(pycache_path) and os.path.isdir(pycache_path):
        try:
            shutil.rmtree(pycache_path)
            print("Deleted __pycache__ folder.")
        except Exception as e:
            print(f"Error deleting __pycache__: {e}")


this_script_dir = os.path.dirname(os.path.abspath(__file__))
# Register the cleanup function to run at script exit
atexit.register(remove_pycache)

if __name__ == "__main__":
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
