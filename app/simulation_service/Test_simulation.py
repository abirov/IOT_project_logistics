from pymongo import MongoClient
import paho.mqtt.publish as publish
import time, random, json
from datetime import datetime

# ==== CONFIGURATION ====
mongo_uri = "mongodb://mongo:27017/"
mqtt_broker = "mosquitto"
mqtt_port = 1883
topic_prefix = "location/vehicle"
interval_seconds = 10
refresh_every_n_cycles = 6

LAT_MIN, LAT_MAX = 45.0410, 45.0910
LON_MIN, LON_MAX = 7.6350, 7.7050

def generate_random_coordinate(prev_lat=None, prev_lon=None, step=0.0005):
    if prev_lat is None or prev_lon is None:
        return round(random.uniform(LAT_MIN, LAT_MAX), 6), round(random.uniform(LON_MIN, LON_MAX), 6)
    lat = min(max(prev_lat + random.uniform(-step, step), LAT_MIN), LAT_MAX)
    lon = min(max(prev_lon + random.uniform(-step, step), LON_MIN), LON_MAX)
    return round(lat, 6), round(lon, 6)

def get_vehicle_ids_from_mongo():
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client["IOT"]
        collection = db["driver"]
        vehicle_ids = []
        for doc in collection.find({}, {"vehicle_id": 1}):
            if "vehicle_id" in doc:
                vehicle_ids.append(doc["vehicle_id"])
        print("Vehicle IDs fetched from MongoDB:", vehicle_ids)
        return vehicle_ids
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return []

# ==== MAIN ====
print(" Simulator starting... connecting to MongoDB & MQTT.")

vehicle_ids = get_vehicle_ids_from_mongo()
if not vehicle_ids:
    print("No vehicle IDs found. Exiting.")
    exit(1)

positions = {vid: generate_random_coordinate() for vid in vehicle_ids}
print("Starting publishing loop...")

cycle = 0
try:
    while True:
        if cycle % refresh_every_n_cycles == 0:
            updated_ids = get_vehicle_ids_from_mongo()
            if set(updated_ids) != set(vehicle_ids):
                print(f" Vehicle ID list updated: {updated_ids}")
                vehicle_ids = updated_ids
                for vid in vehicle_ids:
                    if vid not in positions:
                        positions[vid] = generate_random_coordinate()

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
            print("ON", payload)
            publish.single(f"{topic_prefix}/{vid}", payload=payload,
                           hostname=mqtt_broker, port=mqtt_port)
            positions[vid] = (lat, lon)

        cycle += 1
        time.sleep(interval_seconds)

except KeyboardInterrupt:
    print("\n Simulator stopped")
