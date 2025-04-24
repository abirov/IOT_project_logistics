import time
import random
import json
from datetime import datetime
import paho.mqtt.publish as publish



vehicle_ids = ["vehicle_1", "vehicle_2", "vehicle_3"]  # predefined vehicles

broker = "test.mosquitto.org"
port = 1883
topic = "vehicle/position"
interval_seconds = 120  # Update every 2 minutes

# Torino bounding box (approximate but accurate)
LAT_MIN, LAT_MAX = 45.0410, 45.0910
LON_MIN, LON_MAX = 7.6350, 7.7050



def generate_random_coordinate(prev_lat=None, prev_lon=None, step=0.0005):
    """Generate random coordinates, simulating small vehicle movement."""
    if prev_lat is None or prev_lon is None:
        lat = round(random.uniform(LAT_MIN, LAT_MAX), 6)
        lon = round(random.uniform(LON_MIN, LON_MAX), 6)
    else:
        lat = round(min(max(prev_lat + random.uniform(-step, step), LAT_MIN), LAT_MAX), 6)
        lon = round(min(max(prev_lon + random.uniform(-step, step), LON_MIN), LON_MAX), 6)
    return lat, lon



# Initialize each vehicle with a random starting position
positions = {vid: generate_random_coordinate() for vid in vehicle_ids}

print("Vehicle simulator started! Publishing every 2 minutes...\n")

try:
    while True:
        for vehicle_id in vehicle_ids:
            prev_lat, prev_lon = positions[vehicle_id]
            lat, lon = generate_random_coordinate(prev_lat, prev_lon)

            data = {
                "vehicle_id": vehicle_id,
                "latitude": lat,
                "longitude": lon,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            payload = json.dumps(data)
            print(f"📡 Sending → {payload}")
            publish.single(topic, payload=payload, hostname=broker, port=port)

            # Update the last known position
            positions[vehicle_id] = (lat, lon)

        time.sleep(interval_seconds)

except KeyboardInterrupt:
    print("\n🛑 Simulation stopped by user.")