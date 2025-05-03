import cherrypy
import cherrypy_cors
import json
from DBconnectore3 import influxdbmanager

class influxconnectoreServer:
    exposed = True

    def __init__(self):
        self.influxdb = influxdbmanager('configinfluxdb.json')
    
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if uri and uri[0] == 'location':
            vehicle_id = params.get('vehicle_id')
            period = params.get('period')
            if vehicle_id and period:
                location = self.influxdb.get_location(vehicle_id, period)
                # Build list of points (instead of bad JSON columns)
                points = []
                for idx, row in location.iterrows():
                    points.append({
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "time": row["time"]
                    })
                return points
            else:
                return {"error": "Missing vehicle_id or period parameter"}

        elif uri and uri[0] == 'vehicle':
            latitude = params.get('latitude')
            longitude = params.get('longitude')
            period = params.get('period')
            if latitude and longitude and period:
                vehicle = self.influxdb.get_vehicle_by_location(latitude, longitude, period)
                points = []
                for idx, row in vehicle.iterrows():
                    points.append({
                        "vehicle_id": row["vehicle_id"],
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "time": row["time"]
                    })
                return points
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
                points = []
                for idx, row in vehicles.iterrows():
                    points.append({
                        "vehicle_id": row["vehicle_id"],
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "time": row["time"]
                    })
                return points
            else:
                return {"error": "Missing latitude/longitude range or period parameter"}

        elif uri and uri[0] == 'allvehicles':
            period = params.get('period')
            if period:
                vehicles = self.influxdb.show_all_vehicles_on_map(period)
                points = []
                for idx, row in vehicles.iterrows():
                    points.append({
                        "vehicle_id": row["vehicle_id"],
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "time": row["time"]
                    })
                return points
            else:
                return {"error": "Missing period parameter"}
            
        elif uri and uri[0] == 'calculate_distance':
            vehicle_id = params.get('vehicle_id')
            period = params.get('period')
            if vehicle_id and period:
                distance = self.influxdb.calculate_distance(vehicle_id, period)
                return {"distance": distance}
            else:
                return {"error": "Missing vehicle_id or period parameter"}
            
        elif uri and uri[0] == 'MeanSpeed':
            vehicle_id = params.get('vehicle_id')
            period = params.get('period')
            if vehicle_id and period:
                mean_speed = self.influxdb.MeanSpeed(vehicle_id, period)
                return {"mean_speed": mean_speed}
            else:
                return {"error": "Missing vehicle_id or period parameter"}

        return {"error": "Invalid URI"} 

if __name__ == '__main__':
    cherrypy_cors.install()

    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': False,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'application/json')],
        }
    }

    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8083})

    cherrypy.tree.mount(influxconnectoreServer(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()