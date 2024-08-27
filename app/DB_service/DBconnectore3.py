import influxdb_client
from influxdb_client import Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import configparser
import os
import json

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

    def write_data(self,measurement, tags, fields, time):
        point = Point(measurement)
        for tag_key, tag_value in tags.items():
            point = point.tag(tag_key, tag_value)
        for field_key, field_value in fields.items():
            point = point.field(field_key, field_value)
        point = point.time(time, WritePrecision.NS)
        self.write_api.write(bucket=self.influxdb_bucket, org=self.influxdb_org, record=point)
        print("Data written to InfluxDB")

    def get_location(self, vehicle_id, period):
        query = (f'from(bucket: "{self.influxdb_bucket}") '
                 f'|> range(start: -{period}) '
                 f'|> filter(fn: (r) => r._measurement == "vehicle" '
                 f'and r.vehicle_id == "{vehicle_id}") '
                 f'|> sort(columns: ["_time"], desc: true)')
        location = self.query_api.query_data_frame(query)
        return location , vehicle_id
    
    def get_vehicle_by_location(self, latitude, longitude, period):
        query = (f'from(bucket: "{self.influxdb_bucket}") '
                 f'|> range(start: -{period}) '
                 f'|> filter(fn: (r) => r._measurement == "vehicle" '
                 f'and r.latitude == {latitude} '
                 f'and r.longitude == {longitude}) '
                 f'|> sort(columns: ["_time"], desc: true)')
        vehicle = self.query_api.query_data_frame(query)
        return vehicle
    
    def get_vehicles_by_location(self, min_latitude, max_latitude, min_longitude, max_longitude, period):
        query = (f'from(bucket: "{self.influxdb_bucket}") '
                f'|> range(start: -{period}) '
                f'|> filter(fn: (r) => r._measurement == "vehicle" '
                f'and r.latitude >= {min_latitude} '
                f'and r.latitude <= {max_latitude} '
                f'and r.longitude >= {min_longitude} '
                f'and r.longitude <= {max_longitude}) '
                f'|> sort(columns: ["_time"], desc: true)')
        vehicle = self.query_api.query_data_frame(query)
        return vehicle
    
    def show_all_vehicles_on_map(self, period):
        query = (f'from(bucket: "{self.influxdb_bucket}") '
                f'|> range(start: -{period}) '
                f'|> filter(fn: (r) => r._measurement == "vehicle") '
                f'|> sort(columns: ["_time"], desc: true)')
        vehicles = self.query_api.query_data_frame(query)
        return vehicles
    
    def close(self):
        self.client.close()
        print("InfluxDB connection closed")
