from fastapi import FastAPI, HTTPException, UploadFile, File
from models import (
    Coords,
    Route,
    Station,
    update_routes_locations,
    stations_dict,
    routes_dict,
    routes_list,
    stations_dict_by_names,
)
import asyncio
from contextlib import asynccontextmanager
import uvicorn
import math
import os
import shutil
import atexit
from shapely.geometry import Point, shape, MultiLineString
import json
import unicodedata
import tempfile
import openai
from openai import OpenAI

OPENAI_API_KEY='' #FIXME Pongan mi API Key the OpenAI, la mande por WhatsApp :) Att: Sergio
client = OpenAI(api_key=OPENAI_API_KEY)

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

@app.get("/stations/{id}", response_model=Station)
async def read_station(id: int):
    print(f"Searching for station with id={id}")
    station = stations_dict.get(id, None)
    if not station:
        raise HTTPException(status_code=404, detail=f"Station with id={id} not found")
    return station

@app.post("/stations/nearest_station", response_model=Station)
async def read_nearest_station(coords: Coords):
    nearest_station = None
    R = 6371000
    nearest_distance = math.inf

    lat1, lon1 = coords.latitude, coords.longitude

    for station in stations_dict.values():
        lat2, lon2 = station.latitude, station.longitude
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        if distance < nearest_distance:
            nearest_station = station
            nearest_distance = distance

    if nearest_station is None:
        raise HTTPException(status_code=404, detail=f"No stations found")

    try:
        with open("api\\data\\Rutas_Troncales_de_TRANSMILENIO.geojson", encoding="utf-8") as f:
            routes_geojson = json.load(f)

        station_point = Point(nearest_station.longitude, nearest_station.latitude)
        arriving_routes = []

        for feature in routes_geojson["features"]:
            geometry = feature.get("geometry")
            if geometry["type"] != "MultiLineString":
                continue
            geom = shape(geometry)
            route_distance = geom.distance(station_point)

            properties = feature.get("properties")
            nombre_ruta = properties.get("nombre_ruta_troncal")
            destino = properties.get("destino_ruta_troncal")

            if route_distance < 0.0015:
                route_id = properties.get("objectid") or hash(json.dumps(feature["geometry"]))
                raw_route_name = nombre_ruta or "SIN_NOMBRE"
                route_name = raw_route_name.split()[0] if raw_route_name.strip() else "SIN_NOMBRE"

                destino_normalized = unicodedata.normalize("NFKD", destino or "").encode("ascii", "ignore").decode("ascii")
                destino_key = destino_normalized.replace(" ", "_").lower()
                destination_station = stations_dict_by_names.get(destino_key)
                destination_id = destination_station.id if destination_station else -1

                arriving_routes.append(
                    Route(id=route_id, name=route_name, destinationStationId=destination_id)
                )

        print(f"Station '{nearest_station.name}' matched {len(arriving_routes)} routes.")
        nearest_station.arrivingRoutes = arriving_routes

    except Exception as e:
        print("Failed to compute arriving routes:", e)
        nearest_station.arrivingRoutes = []

    return nearest_station

@app.post("/voice/route")
async def transcribe_and_extract_route(audio: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as file_obj:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=file_obj,
                prompt="Transcribe only the name of the TransMilenio route. Focus on names like B10, J24, 6, etc. The message is in Spanish. In the response please show only 'J24', '6', and so on "
            )

        os.remove(tmp_path)
        return {"route": transcript.text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def remove_pycache():
    pycache_path = os.path.join(this_script_dir, "__pycache__")
    if os.path.exists(pycache_path) and os.path.isdir(pycache_path):
        try:
            shutil.rmtree(pycache_path)
            print("Deleted __pycache__ folder.")
        except Exception as e:
            print(f"Error deleting __pycache__:", e)

this_script_dir = os.path.dirname(os.path.abspath(__file__))
atexit.register(remove_pycache)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
