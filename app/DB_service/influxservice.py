import cherrypy
import cherrypy_cors
import json
from DBconnectore3 import influxdbmanager

class influxconnectoreServer:
    exposed = True  # Required when using MethodDispatcher

    def __init__(self):
        self.influxdb = influxdbmanager('configinfluxdb.json')

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if uri and uri[0] == 'location':
            vehicle_id = params.get('vehicle_id')
            period = params.get('period')
            if vehicle_id and period:
                location = self.influxdb.get_location(vehicle_id, period)
                location_json = location.to_json(orient='columns')
                return location_json
            else:
                return {"error": "Missing vehicle_id or period parameter"}

        elif uri and uri[0] == 'vehicle':
            latitude = params.get('latitude')
            longitude = params.get('longitude')
            period = params.get('period')
            if latitude and longitude and period:
                vehicle = self.influxdb.get_vehicle_by_location(latitude, longitude, period)
                vehicle_json = vehicle.to_json(orient='columns')
                return vehicle_json
            else:
                return {"error": "Missing latitude, longitude, or period parameter"}

        elif uri and uri[0] == 'vehicles':
            min_latitude = params.get('min_latitude')
            max_latitude = params.get('max_latitude')
            min_longitude = params.get('min_longitude')
            max_longitude = params.get('max_longitude')
            period = params.get('period')
            if min_latitude and max_latitude and min_longitude and max_longitude and period:
                vehicles = self.influxdb.get_vehicles_by_location(min_latitude, max_latitude, min_longitude, max_longitude, period)
                vehicles_json = vehicles.to_json(orient='columns')
                return vehicles_json
            else:
                return {"error": "Missing latitude/longitude range or period parameter"}

        else:
            return {"error": "Invalid URI"}

if __name__ == '__main__':
    # Enable CORS
    cherrypy_cors.install()

    # Configuration for MethodDispatcher and disabling sessions to avoid session issues
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': False,  # Disable sessions if not needed
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    }

    # Update the socket configuration
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})

    # Start the server with the configuration
    cherrypy.tree.mount(influxconnectoreServer(), '/', conf)
    cherrypy.engine.start()
