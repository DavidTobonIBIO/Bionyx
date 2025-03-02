from fastapi import FastAPI, HTTPException
from models import Station, update_bus_locations, stations_dict, Coords
import asyncio
from contextlib import asynccontextmanager
import uvicorn
from sklearn.metrics.pairwise import haversine_distances


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up and launching background tasks...")
    task = asyncio.create_task(update_bus_locations())
    yield
    task.cancel()
    print("Shutting down.")


app = FastAPI(root_path="/api", lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "Bus API"}


@app.get("/stations/", response_model=list[Station])
async def read_stations():
    return list(stations_dict.values())


@app.get("/stations/{name}", response_model=Station)
async def read_station(name: str):
    if name not in stations_dict:
        raise HTTPException(status_code=404, detail=f"Station {name} not found")
    return stations_dict[name]

@app.post("/nearest_station/", response_model=Station)
async def read_nearest_station(coords: Coords):
    
    x1 = [coords.lat, coords.lon]
    nearest_station = None
    nearest_distance = 4.5 # 4.5 km is the maximum distance between two stations
    for station in stations_dict.values():
        x2 = [station.lat, station.lon]
        distance = haversine_distances([x1, x2])[0][1]
        distance_in_km = distance * 6371 # 6371 is the radius of the Earth
        if distance_in_km < nearest_distance:
            nearest_station = station
            nearest_distance = distance
            return nearest_station
        else:
            raise HTTPException(status_code=404, detail=f"No nearest station found")


if __name__ == "__main__":
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
