import requests
import json
from dotenv import load_dotenv
import os

# Define the API URL
url = "https://routes.googleapis.com/directions/v2:computeRoutes"

# Load environment variables from .env.local file
load_dotenv(dotenv_path='.env')

# Get the API key from the environment variable
API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')


# Define headers
headers = {
    "Content-Type": "application/json",
    "X-Goog-Api-Key": API_KEY,
    "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs",
}

# Define the request payload
data = {
    "origin": {"location": {"latLng": {"latitude": 4.58598283, "longitude": -74.20546046}}},
    "destination": {"location": {"latLng": {"latitude": 4.65729068, "longitude": -74.07766289}}},
    "travelMode": "TRANSIT",
    "computeAlternativeRoutes": True,
}

# Send the POST request
response = requests.post(url, json=data, headers=headers)
print(response.json())
# Save the response as a pickle file
with open("response.json", "w", encoding="utf-8") as f:
    json.dump(response.json(), f, indent=4)
