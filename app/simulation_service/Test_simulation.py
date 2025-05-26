import time, random, json
from datetime import datetime
import paho.mqtt.publish as publish

# ==== CONFIGURATION ====
vehicle_ids = [
    "af91581d-a0b2-4b96-a67c-73b46383c14f",
    "09102cd8-c063-4af1-8269-3b29f137d975",
    "01759d5f-2bb2-448e-b91d-fa5beefe9fd9",
    "b4615184-2e1b-40be-aa07-9b1882a35955"   # <<< my VEHICLE
]

broker = "mosquitto"

port            = 1883
topic_prefix           = "location/vehicle"
interval_seconds= 10    # 1 min

# Torino bounding box
LAT_MIN, LAT_MAX = 45.0410, 45.0910
LON_MIN, LON_MAX = 7.6350, 7.7050

def generate_random_coordinate(prev_lat=None, prev_lon=None, step=0.0005):
    if prev_lat is None or prev_lon is None:
        return round(random.uniform(LAT_MIN, LAT_MAX), 6), round(random.uniform(LON_MIN, LON_MAX), 6)
    lat = min(max(prev_lat + random.uniform(-step, step), LAT_MIN), LAT_MAX)
    lon = min(max(prev_lon + random.uniform(-step, step), LON_MIN), LON_MAX)
    return round(lat, 6), round(lon, 6)

# initialize positions
positions = {vid: generate_random_coordinate() for vid in vehicle_ids}

print("🚀 Simulator started — publishing to", broker)

try:
    while True:
        for vid in vehicle_ids:
            prev_lat, prev_lon = positions[vid]
            lat, lon = generate_random_coordinate(prev_lat, prev_lon)
            msg = {
                "vehicle_id": vid,
                "latitude": lat,
                "longitude": lon,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "measurement": "LOCATION"
            }
            payload = json.dumps(msg)
            print("📡", payload)
            publish.single(f"{topic_prefix}/{vid}", payload=payload,
                           hostname=broker, port=port)
            positions[vid] = (lat, lon)
        time.sleep(interval_seconds)
except KeyboardInterrupt:
    print("\n🛑 Simulator stopped")
