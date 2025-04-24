import influxdb_client
from influxdb_client import Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import os
import json
import pandas as pd
from math import radians, sin, cos, sqrt, atan2

class influxdbmanager:
    def __init__(self, config_file):
        config = {}
        path = os.path.join(os.path.dirname(__file__), config_file)
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = json.load(f)
        
        self.influxdb_url = config['url']
        self.influxdb_token = config['token']
        self.influxdb_org = config['org']
        self.influxdb_bucket = config['bucket']

        # Initialize InfluxDB client
        self.client = influxdb_client.InfluxDBClient(
            url=self.influxdb_url,
            token=self.influxdb_token,
            org=self.influxdb_org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.delete_api = self.client.delete_api()

    def write_data(self, measurement, tags, fields, time):
        point = Point(measurement)
        for tag_key, tag_value in tags.items():
            point = point.tag(tag_key, tag_value)
        for field_key, field_value in fields.items():
            if isinstance(field_value, float):
                point = point.field(field_key, round(field_value, 20))  # Ensures up to 20 decimal places
            else:
                point = point.field(field_key, field_value)
        point = point.time(time, WritePrecision.NS)
        self.write_api.write(bucket=self.influxdb_bucket, org=self.influxdb_org, record=point)
        print("Data written to InfluxDB")


    def get_location(self, vehicle_id, period):
        
        #Returns a pandas DataFrame of all points for vehicle_id 
        #in the last `period` 
      
        query = f'''
        from(bucket: "{self.influxdb_bucket}")
          |> range(start: -{period})
          |> filter(fn: (r) => r["_measurement"] == "LOCATION" and r["vehicle_id"] == "{vehicle_id}")
          |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
          |> keep(columns: ["_time", "latitude", "longitude"])
          |> sort(columns: ["_time"], desc: true)
        '''
        tables = self.query_api.query(query)

        result = []
        for table in tables:
            for record in table.records:
                result.append({
                    "time": record["_time"].isoformat(),
                    "latitude": float(record["latitude"]),
                    "longitude": float(record["longitude"])
                })

        df = pd.DataFrame(result)
        print(f"DEBUG get_location('{vehicle_id}','{period}') → {len(df)} rows")  # <— debug
        return df

    
    def get_vehicle_by_location(self, latitude, longitude, period):
        latitude = float(latitude)
        longitude = float(longitude)
        query = (f'from(bucket: "{self.influxdb_bucket}") '
                f'|> range(start: -{period}) '
                f'|> filter(fn: (r) => r._measurement == "vehicle") '
                f'|> filter(fn: (r) => r.latitude >= {latitude}) '
                f'|> filter(fn: (r) => r.longitude >= {longitude}) '
                f'|> sort(columns: ["_time"], desc: true) '
                f'|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")')

        print("Running query:", query)  # Debugging: Print the query
        vehicle = self.query_api.query_data_frame(query)
        print("Query result:", vehicle)  # Debugging: Print the raw result
        
        return vehicle



    
    def get_vehicles_by_location(self, min_latitude, max_latitude, min_longitude, max_longitude, period):
        query = (f'from(bucket: "{self.influxdb_bucket}") '
                f'|> range(start: -{period}) '
                f'|> filter(fn: (r) => r._measurement == "vehicle" '
                f'and r.latitude >= {min_latitude} '
                f'and r.latitude <= {max_latitude} '
                f'and r.longitude >= {min_longitude} '
                f'and r.longitude <= {max_longitude}) '
                f'|> sort(columns: ["_time"], desc: true)'
                f'|>pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")')
        vehicles = self.query_api.query_data_frame(query)
        print("Query result:", vehicles)  # Debugging: Print the raw result 
        return vehicles
    
    def show_all_vehicles_on_map(self, period):
        query = (f'from(bucket: "{self.influxdb_bucket}") '
                f'|> range(start: -{period}) '
                f'|> filter(fn: (r) => r._measurement == "vehicle") '
                f'|> sort(columns: ["_time"], desc: true)'
                f'|>pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")')
        vehicles = self.query_api.query_data_frame(query)
        return vehicles
    

    # post process query for more complex functionality


    def get_vehicle_path(self, vehicle_id, period):
        query = f"""
        from(bucket: "{self.influxdb_bucket}")
            |> range(start: -{period})
            |> filter(fn: (r) => r["_measurement"] == "vehicle" and r["vehicle_id"] == "{vehicle_id}")
            |> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")
            |> keep(columns: ["_time", "latitude", "longitude"])
            |> sort(columns: ["_time"], desc: true)
        """
        df = self.query_api.query_data_frame(query)
        return df
    


    def calculate_distance(self, vehicle_id, period):
        df = self.get_vehicle_path(vehicle_id, period)
        if df.empty or len(df) < 2:
            return 0.0

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371000  # Earth radius in meters
            phi1 = radians(lat1)
            phi2 = radians(lat2)
            delta_phi = radians(lat2 - lat1)
            delta_lambda = radians(lon2 - lon1)

            a = sin(delta_phi / 2)**2 + cos(phi1) * cos(phi2) * sin(delta_lambda / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c  # distance in meters

        distances = []
        for i in range(1, len(df)):
            lat1, lon1 = df.iloc[i - 1]['latitude'], df.iloc[i - 1]['longitude']
            lat2, lon2 = df.iloc[i]['latitude'], df.iloc[i]['longitude']
            distance = haversine(lat1, lon1, lat2, lon2)
            distances.append(distance)
        total_distance = sum(distances)
        return total_distance

    def MeanSpeed(self, vehicle_id, period):
        df = self.get_vehicle_path(vehicle_id, period)
        if df.empty or len(df) < 2:
            return 0.0

        total_distance = self.calculate_distance(vehicle_id, period)
        time_diff = (df.iloc[0]['_time'] - df.iloc[-1]['_time']).total_seconds() / 3600
        if time_diff == 0:
            return 0.0
        mean_speed = total_distance / time_diff  # in meters per hour
        return mean_speed/1000         # convert to km/h

    
    def close(self):
        self.client.close()
        print("InfluxDB connection closed")


if __name__ == '__main__':
        influxdb = influxdbmanager('configinfluxdb.json')
        influxdb.write_data('vehicle', {'vehicle_id': 'vehicle20933'}, {'latitude': 39.7749, 'longitude': -150.4194}, '2024-09-12T16:00:00Z')
        location, vehicle_id = influxdb.get_location('vehicle9', '720')
        print(location)
#         location, vehicle_id = influxdb.get_location('vehicle11', '720')
#         print(location)
#         # columns = location.columns
#         # print("Columns:", columns)
#         # print(location)
#         # vehicle = influxdb.get_vehicle_by_location(138.7749, -28.4194, '2')
#         # print(vehicle)
#         # vehicles = influxdb.get_vehicles_by_location(137.7749, 147.7750, -29.4194, -30.4193, '100h')
#         # print(vehicles)
#         # vehicles = influxdb.show_all_vehicles_on_map('100')
#         # print(vehicles)
#         influxdb.close()
