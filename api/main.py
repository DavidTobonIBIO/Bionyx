from fastapi import FastAPI, HTTPException, UploadFile, File
import re
from models import Coordinates, Route, Station
from load_data import load_data, sentence_model, create_stop_embedding_cache
import uvicorn
import math
import os
import shutil
import atexit
import tempfile
import logging
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import torch

from sentence_transformers import util

# Set up logging
log_dir = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"api_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    filename=log_file,
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv(dotenv_path=".env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    error_msg = "OPENAI_API_KEY not found in .env file"
    logger.error(f"HTTP 500: {error_msg}")
    raise ValueError(error_msg)
client: OpenAI = OpenAI(api_key=OPENAI_API_KEY)

stations_dict, stations_dict_by_names, routes_dict, routes_list, route_station_mapping  = load_data()
embedding_cache = create_stop_embedding_cache(route_station_mapping)

route_names = [route.name for route in routes_list] # used for the prompt to whisper

app = FastAPI(root_path="/api")


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "OrientApp Backend"}


@app.get("/routes/", response_model=list[Route])
async def read_routes_names() -> list[Route]:
    if routes_list:
        return routes_list
    else:
        error_msg = "No routes found"
        logger.error(f"HTTP 404: {error_msg}")
        raise HTTPException(status_code=404, detail=error_msg)


@app.get("/routes/{id}", response_model=Route)
async def read_route(id: int) -> Route:
    route = routes_dict.get(id)
    if route:
        return route
    else:
        error_msg = f"Route with id={id} does not exist"
        logger.error(f"HTTP 404: {error_msg}")
        raise HTTPException(
            status_code=404, detail=error_msg
        )


@app.get("/stations/", response_model=list[Station])
async def read_stations() -> list[Station]:
    if stations_dict:
        return list(stations_dict.values())
    else:
        error_msg = "No stations found"
        logger.error(f"HTTP 404: {error_msg}")
        raise HTTPException(status_code=404, detail=error_msg)


@app.get("/stations/{id}", response_model=Station)
async def read_station(id: int) -> Station:
    print(f"Searching for station with id={id}")
    station = stations_dict.get(id, None)
    if not station:
        error_msg = f"Station with id={id} does not exist"
        logger.error(f"HTTP 404: {error_msg}")
        raise HTTPException(
            status_code=404, detail=error_msg
        )
    return station

@app.post("/stations/nearest_station", response_model=Station)
async def read_nearest_station(coords: Coordinates) -> Station:
    nearest_station: Station | None = None
    R: float = 6371000
    nearest_distance: float = 400  # in meters

    lat1, lon1 = coords.latitude, coords.longitude

    for station in stations_dict.values():
        lat2, lon2 = station.coordinates.latitude, station.coordinates.longitude
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        if distance < nearest_distance:
            nearest_station = station
            nearest_distance = distance

    if nearest_station is None:
        error_msg = "No near station found"
        logger.error(
            f"HTTP 404: {error_msg} for coordinates: lat={coords.latitude}, lon={coords.longitude}"
        )
        raise HTTPException(status_code=404, detail=error_msg)
    
    threshold = 0.65
    station_embedding = sentence_model.encode(
        nearest_station.name, convert_to_tensor=True
    )

    filtered_routes = []
    print(nearest_station.arrivingRoutes)
    for route in nearest_station.arrivingRoutes:
        route_name = route.name.upper()

        if route_name not in embedding_cache:
            continue

        stop_data = embedding_cache[route_name]
        stop_names = stop_data["stops"]
        stop_embeddings = stop_data["embeddings"]

        scores = util.cos_sim(station_embedding, stop_embeddings)
        max_score = scores.max().item()
        best_stop = stop_names[scores.argmax().item()]

        # print(f"[{route_name}] Match: {best_stop} (score={max_score:.2f})")

        if max_score >= threshold:
            print(f"Added to routes!")
            print(f"[{route_name}] Match: {best_stop} (score={max_score:.2f})")
            filtered_routes.append(route)
        
        nearest_station.arrivingRoutes = filtered_routes
                    
    return nearest_station


@app.post("/voice/route", response_model=list[Route])
async def transcribe_and_extract_route(audio: UploadFile = File(...)) -> dict[str, any]:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await audio.read())
            tmp_path: str = tmp.name

        with open(tmp_path, "rb") as file_obj:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=file_obj,
                prompt=", ".join(route_names),
            )

        os.remove(tmp_path)

        # Clean the transcription result
        raw_text: str = transcript.text.strip().upper()
        match = re.search(r"\b([A-Z]?\d{1,2})\b", raw_text) # optional letter followed by 1 or 2 digits
        if not match:
            error_msg = "No valid route substring detected"
            logger.error(f"HTTP 404: {error_msg} for transcription: '{raw_text}'")
            raise HTTPException(status_code=404, detail=error_msg)

        detected_route_name: str = match.group(1).upper()
        print("Detected route name:", detected_route_name)
        
        matching_routes: list[Route] = []
        for route in routes_list:
            if route.name == detected_route_name:
                matching_routes.append(route)

        if len(matching_routes) == 0:
            error_msg = f"No matching route found for '{detected_route_name}'"
            logger.error(f"HTTP 404: {error_msg}")
            raise HTTPException(status_code=404, detail="No matching route found.")

        return matching_routes

    except Exception as e:
        error_msg = str(e)
        logger.error(f"HTTP 500: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

def remove_pycache() -> None:
    pycache_path: str = os.path.join(this_script_dir, "__pycache__")
    if os.path.exists(pycache_path) and os.path.isdir(pycache_path):
        try:
            shutil.rmtree(pycache_path)
            print("Deleted __pycache__ folder.")
        except Exception as e:
            print(f"Error deleting __pycache__:", e)


this_script_dir: str = os.path.dirname(os.path.abspath(__file__))
atexit.register(remove_pycache)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
