import cherrypy
import cherrypy_cors
from DBconnectore3 import influxdbmanager

class influxconnectoreServer:
    exposed = True  
    def __init__(self):
        self.influxdb = influxdbmanager('configinfluxdb.json')

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if not uri:
            return {"error": "Invalid URI"}

        endpoint = uri[0]

        
        #    Returns the timestamped lat/lon history for a single vehicle over the past period (e.g. '2h')
        #    Params: vehicle_id, period
        if endpoint == 'location':
            vehicle_id = params.get('vehicle_id')
            period     = params.get('period')
            if not vehicle_id or not period:
                return {"error": "Missing vehicle_id or period parameter"}
            df = self.influxdb.get_location(vehicle_id, period)
            # return a Python list of dicts
            return df.to_dict(orient='records')

        # Finds any vehicle points whose latitude >= `latitude` AND longitude >= `longitude`
        # within the last period
        # Params: latitude, longitude, period
        elif endpoint == 'vehicle':
            lat    = params.get('latitude')
            lon    = params.get('longitude')
            period = params.get('period')
            if not lat or not lon or not period:
                return {"error": "Missing latitude, longitude, or period parameter"}
            df = self.influxdb.get_vehicle_by_location(lat, lon, period)
            return df.to_dict(orient='records')

        #Returns all vehicle points that fall inside the box defined by:
        #      min_latitude ≤ lat ≤ max_latitude
        #      min_longitude ≤ lon ≤ max_longitude
       
        elif endpoint == 'vehicles':
            min_lat = params.get('min_latitude')
            max_lat = params.get('max_latitude')
            min_lon = params.get('min_longitude')
            max_lon = params.get('max_longitude')
            period  = params.get('period')
            if not (min_lat and max_lat and min_lon and max_lon and period):
                return {"error": "Missing latitude/longitude range or period parameter"}
            df = self.influxdb.get_vehicles_by_location(min_lat, max_lat, min_lon, max_lon, period)
            return df.to_dict(orient='records')

        #history_all
        #Params: period
        elif endpoint == 'allvehicles':
            period = params.get('period')
            if not period:
                return {"error": "Missing period parameter"}
            df = self.influxdb.show_all_vehicles_on_map(period)
            return df.to_dict(orient='records')

        else:
            return {"error": "Invalid URI"}


if __name__ == '__main__':
    # Enable CORS
    cherrypy_cors.install()

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': False,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    }

    cherrypy.config.update({
        'server.socket_host': '0.0.0.0',
        'server.socket_port': 8084
    })
    cherrypy.tree.mount(influxconnectoreServer(), '/', conf)
    cherrypy.engine.start()
