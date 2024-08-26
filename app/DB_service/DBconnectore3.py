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

    def write_data(self, data, tags, fields, time):
        point = Point(data)
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
                 f'|> filter(fn: (r) => r._data == "location" '
                 f'and r.vehicle_id == "{vehicle_id}") '
                 f'|> sort(columns: ["_time"], desc: true)')
        location = self.query_api.query_data_frame(query)
        return location

    def close(self):
        self.client.close()
        print("InfluxDB connection closed")
