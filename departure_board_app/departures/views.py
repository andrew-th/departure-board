from django.shortcuts import render
from django.http import JsonResponse
import requests
from datetime import datetime, timedelta

# TODO secure api data
TRANSIT_API_URL = "https://transit.api/gtfs-rt"
API_KEY = "your_api_key"

# render the frontend
def index(request):
    return render(request, "departures/index.html")

# fetch GTFS data
def fetch_gtfs_data(stop_id):
    try:
        response = requests.get(
            f"{TRANSIT_API_URL}",
            params={"stop": stop_id, "key": API_KEY},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching GTFS data: {e}")
        return None

# process GTFS data
def process_departures(data):
    departures = []
    now = datetime.now()
    for trip in data.get("entity", []):
        if "trip_update" in trip:
            stop_time_updates = trip["trip_update"].get("stop_time_update", [])
            for update in stop_time_updates:
                stop_id = update.get("stop_id")
                arrival = update.get("arrival", {}).get("time")

                if arrival:
                    arrival_time = datetime.fromtimestamp(int(arrival))
                    time_to_departure = (arrival_time - now).total_seconds() // 60

                    departures.append({
                        "route": trip["trip_update"].get("trip", {}).get("route_id"),
                        "destination": trip["trip_update"].get("trip", {}).get("trip_headsign"),
                        "scheduled_time": arrival_time.strftime("%I:%M %p"),
                        "countdown": int(time_to_departure),
                    })

    return sorted(departures, key=lambda x: x["countdown"])

# fetch departures
def get_departures(request):
    stop_id = request.GET.get("stopId")

    if not stop_id:
        return JsonResponse({"error": "Missing stopId parameter."}, status=400)

    gtfs_data = fetch_gtfs_data(stop_id)

    if not gtfs_data:
        return JsonResponse({"error": "Failed to fetch GTFS data."}, status=500)

    departures = process_departures(gtfs_data)
    return JsonResponse({"departures": departures})

