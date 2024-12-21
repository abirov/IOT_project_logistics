# test_influxdb.py
import random
from datetime import datetime, timedelta, timezone
from DBconnectore3 import influxdbmanager  # Adjust the import based on your module structure

# Initialize the influxdbmanager
db_manager = influxdbmanager('configinfluxdb.json')  # Adjust the config file path based on your module structure

# Generate random data
def generate_random_data():
    tags = {
        'vehicle_id': f'vehicle_{random.randint(1, 100)}'
    }
    fields = {
        'latitude': random.uniform(-90, 90),
        'longitude': random.uniform(-180, 180),
    }
    time = (datetime.now(timezone.utc) - timedelta(minutes=random.randint(0, 60))).isoformat()
    return tags, fields, time

# Insert random data into InfluxDB
for _ in range(10):  # Insert 10 random data points
    tags, fields, time = generate_random_data()
    db_manager.write_data('vehicle_location', tags, fields, time)