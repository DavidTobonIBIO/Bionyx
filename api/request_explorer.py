import json
from datetime import datetime


def get_time_to_departure(departure_time):
    # departure_time is in the format "HH:MM"
    fmt = "%H:%M"
    current_time = datetime.now().strftime(fmt)
    t1 = datetime.strptime(current_time, fmt)
    t2 = datetime.strptime(departure_time, fmt)
    diff = t2 - t1
    return diff.total_seconds() / 60


with open("response.json", "r") as f:
    response = json.load(f)

users_route = "B12"

for route in response["routes"]:
    leg = route["legs"][0]
    for step in leg["steps"]:
        if step["travelMode"] == "TRANSIT":
            if users_route == step["transitDetails"]["transitLine"]["nameShort"]:
                departure_time = step["transitDetails"]["localizedValues"][
                    "departureTime"
                ]["time"]["text"]
                time_to_departure = get_time_to_departure(departure_time)
                print(f"Your bus will depart in {time_to_departure:.2f} minutes")
