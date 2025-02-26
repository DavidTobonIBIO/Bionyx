from fastapi import FastAPI, HTTPException
from models import Station, stations, update_bus_locations
import asyncio
from contextlib import asynccontextmanager
import uvicorn


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
    return list(stations.values())


@app.get("/stations/{name}", response_model=Station)
async def read_station(name: str):
    if name not in stations:
        raise HTTPException(status_code=404, detail=f"Station {name} not found")
    return stations[name]


if __name__ == "__main__":
    # uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
