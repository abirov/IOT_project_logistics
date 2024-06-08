import cherrypy
from bson import ObjectId
from app.models.logistics_points import (create_logistics_point, get_logistics_point, update_logistics_point, delete_logistics_point, list_logistics_points)
from app.models.vehicles import (create_vehicle, get_vehicle, update_vehicle, delete_vehicle, list_vehicles)
from app.models.drivers import (create_driver, get_driver, update_driver, delete_driver, list_drivers)
from app.models.warehouses import (create_warehouse, get_warehouse, update_warehouse, delete_warehouse, list_warehouses)

class CatalogService:
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def logistics_points(self, point_id=None):
        if cherrypy.request.method == 'GET':
            if point_id:
                point = get_logistics_point(ObjectId(point_id))
                return point
            else:
                points = list_logistics_points()
                return points
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            create_logistics_point(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            update_logistics_point(ObjectId(point_id), data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            delete_logistics_point(ObjectId(point_id))
            return {'status': 'success'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vehicles(self, vehicle_id=None):
        if cherrypy.request.method == 'GET':
            if vehicle_id:
                vehicle = get_vehicle(ObjectId(vehicle_id))
                return vehicle
            else:
                vehicles = list_vehicles()
                return vehicles
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            create_vehicle(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            update_vehicle(ObjectId(vehicle_id), data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            delete_vehicle(ObjectId(vehicle_id))
            return {'status': 'success'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def drivers(self, driver_id=None):
        if cherrypy.request.method == 'GET':
            if driver_id:
                driver = get_driver(ObjectId(driver_id))
                return driver
            else:
                drivers = list_drivers()
                return drivers
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            create_driver(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            update_driver(ObjectId(driver_id), data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            delete_driver(ObjectId(driver_id))
            return {'status': 'success'}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def warehouses(self, warehouse_id=None):
        if cherrypy.request.method == 'GET':
            if warehouse_id:
                warehouse = get_warehouse(ObjectId(warehouse_id))
                return warehouse
            else:
                warehouses = list_warehouses()
                return warehouses
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            create_warehouse(data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            update_warehouse(ObjectId(warehouse_id), data)
            return {'status': 'success'}
        elif cherrypy.request.method == 'DELETE':
            delete_warehouse(ObjectId(warehouse_id))
            return {'status': 'success'}

# Main application to run the services
if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.tree.mount(CatalogService(), '/')
    cherrypy.engine.start()
    cherrypy.engine.block()
