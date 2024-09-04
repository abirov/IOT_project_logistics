import cherrypy
import cherrypy_cors
import pandas as pd
import json
from DBconnectore3 import influxdbmanager
import requests

class influxconnectoreServer:
    exposed = True 

    def __init__(self):
        self.influxdb = influxdbmanager('configinfluxdb.json')

    def GET(self, *uri, **params):
        if uri[0] == 'location':
            vehicle_id = params.get('vehicle_id')
            period = params.get('period')
            location= self.influxdb.get_location(vehicle_id, period)
            
        
        elif uri[0] == 'vehicle':
            latitude = params.get('latitude')
            longitude = params.get('longitude')
            period = params.get('period')
            vehicle = self.influxdb.get_vehicle_by_location(latitude, longitude, period)
            vehicle_json = vehicle.to_json(orient='records')
            return vehicle_json.encode('utf-8')
        
        elif uri[0] == 'vehicles':
            min_latitude = params.get('min_latitude')
            max_latitude = params.get('max_latitude')
            min_longitude = params.get('min_longitude')
            max_longitude = params.get('max_longitude')
            period = params.get('period')
            vehicles = self.influxdb.get_vehicles_by_location(min_latitude, max_latitude, min_longitude, max_longitude, period)
            vehicles_json = vehicles.to_json(orient='records')
            return vehicles_json.encode('utf-8')
        
        else:
            error_message = json.dumps({"error": "Invalid URI"})
            return error_message.encode('utf-8')

# if __name__ == '__main__':
#     conf = {
#         '/': {
#             'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
#             'tools.sessions.on': True,
#             # 'tools.response_headers.on': True,
#             # 'tools.response_headers.headers': [('Content-Type', 'application/json')]
#         }
#     }

#     # config = { "baseUrl": "http://localhost", "basePort": 8080 }
#     # response = requests.get(f'{config["baseUrl"]}{config["basePort"]}/public/fullservices')
#     # services = response.json()
#     # for service in services:
#     #     if service['name'] == 'influxdb':
#     #         config = service
    
#     cherrypy_cors.install()
#     cherrypy.tree.mount(influxconnectoreServer(), '/influxdb', conf)
#     cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
#     cherrypy.engine.start()

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.quickstart(influxconnectoreServer(), '/')