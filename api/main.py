from fastapi import FastAPI, HTTPException
from models import Station, update_bus_locations, stations_dict, Coords
import asyncio
from contextlib import asynccontextmanager
import uvicorn
import math


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

@app.post("/stations/nearest_station", response_model=Station)
async def read_nearest_station(coords: Coords):
    nearest_station = None
    R = 6371000  # Radius of Earth in m
    nearest_distance = 4000 # Nearest distance in m
    
    lat1, lon1 = coords.latitude, coords.longitude
    #print(lat1, lon1)
    for station in stations_dict.values():
        
        lat2, lon2 = station.latitude, station.longitude
        #print(lat2, lon2)
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = math.sin(dphi / 2) * math.sin(dphi / 2) + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) * math.sin(dlambda / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        distance = R * c # Distance in m
        #print(distance)
        
        if distance < nearest_distance:
            nearest_station = station
            nearest_distance = distance
    
    if nearest_station is None:
        raise HTTPException(status_code=404, detail=f"No stations found")

    return nearest_station          

if __name__ == "__main__":
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
