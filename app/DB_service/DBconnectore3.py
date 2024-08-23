import influxdb_client
from influxdb_client import Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json
import os
import configparser


class influxdbmanager:
    def __init__(self, config_file='configinfluxdb.ini'):
        config = configparser.ConfigParser()
        config.read(config_file)

        self.influxdb_url = config['influxdb']['url']
        self.influxdb_token = config['influxdb']['token']
        self.influxdb_org = config['influxdb']['org']
        self.influxdb_bucket = config['influxdb']['bucket']

        self.client = influxdb_client.InfluxDBClient(
            url=self.influxdb_url,
            token=self.influxdb_token,
            org=self.influxdb_org
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.health = self.client.health()
        self.ready = self.health['status'] == 'pass'
        self.status = self.health['status']
        print(self.health)  # print the health status of the influxdb
        self.delete_api = self.client.delete_api()


    def write_data(self,data,tags,fields, time):
        point = Point("location").tag(**tags).field(**fields).time(time, WritePrecision.MS)
        self.write_api.write(bucket=self.influxdb_bucket, record=point)
        


    def get_location(self,vehicle_id, period):
        query = f'from(bucket: "{self.influxdb_bucket}") 
                |> range(start: -{period}) 
                |> filter(fn: (r) => r._measurement == "location" and r.vehicle_id == "{vehicle_id}")
                |> sort(columns: ["_time"], desc: true)'   
        location = self.query_api.query_data_frame(query)
        return location
        

    def close(self):
        self.client.close()
    
