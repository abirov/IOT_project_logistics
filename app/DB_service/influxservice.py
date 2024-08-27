import cherrypy
import cherrypy_cors
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
from datetime import timedelta
import geopandas as gpd
from shapely.geometry import Point
import json
import os
from DBconnectore3 import influxdbmanager

class influxconnectoreServer:
    exposed = True 

    def __init__(self):
        self.influxdb = influxdbmanager('configinfluxdb.json')

    def GET(self, *uri, **params):
        if uri[0] == 'location':
            vehicle_id = params['vehicle_id']
            period = params['period']
            location, vehicle_id = self.influxdb.get_location(vehicle_id, period)
            return location.to_json(orient='records')
        elif uri[0] == 'vehicle':
            latitude = params['latitude']
            longitude = params['longitude']
            period = params['period']
            vehicle = self.influxdb.get_vehicle_by_location(latitude, longitude, period)
            return vehicle.to_json(orient='records')
        elif uri[0] == 'vehicles':
            min_latitude = params['min_latitude']
            max_latitude = params['max_latitude']
            min_longitude = params['min_longitude']
            max_longitude = params['max_longitude']
            period = params['period']
            vehicles = self.influxdb.get_vehicles_by_location(min_latitude, max_latitude, min_longitude, max_longitude, period)
            return vehicles.to_json(orient='records')
        else:
            return "Invalid URI"
    







if __name__ == '__main__':



    dbConnector = influxconnectoreServer()
    serverConf = {
        "url": "localhost",
        "port": 8080
    }
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.sessions.on': True,
        }
    }
    cherrypy.config.update(conf)
    cherrypy.tree.mount(dbConnector, '/influxdb', conf)
    cherrypy_cors.install()
    cherrypy.config.update({'server.socket_host': '0.0.0.0','web.socket_ip': serverConf["url"], 'server.socket_port': serverConf["port"]})
    cherrypy.engine.start()
    # cherrypy.engine.block() #this line blocks the main thread and the code below will not be executed :)


