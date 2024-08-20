import cherrypy
import json
from bson import ObjectId
from pymongo import MongoClient
from models.logistics_point import LogisticsPoint
from models.vehicle import Vehicle
from models.driver import Driver
from models.warehouse import Warehouse
from models.feedback import Feedback

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CatalogService:
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['logistics_db']
        self.logistics_point_model = LogisticsPoint(self.db)
        self.vehicle_model = Vehicle(self.db)
        self.driver_model = Driver(self.db)
        self.warehouse_model = Warehouse(self.db)
        self.feedback_model = Feedback(self.db)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def logistics_points(self, point_id=None):
        if cherrypy.request.method == 'GET':
            if point_id:
                return self.logistics_point_model.get(point_id)
            return self.logistics_point_model.list()
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            return self.logistics_point_model.create(data)
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            return self.logistics_point_model.update(point_id, data)
        elif cherrypy.request.method == 'DELETE':
            return self.logistics_point_model.delete(point_id)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def vehicles(self, vehicle_id=None):
        if cherrypy.request.method == 'GET':
            if vehicle_id:
                return self.vehicle_model.get(vehicle_id)
            return self.vehicle_model.list()
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            return self.vehicle_model.create(data)
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            return self.vehicle_model.update(vehicle_id, data)
        elif cherrypy.request.method == 'DELETE':
            return self.vehicle_model.delete(vehicle_id)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def drivers(self, driver_id=None):
        if cherrypy.request.method == 'GET':
            if driver_id:
                return self.driver_model.get(driver_id)
            return self.driver_model.list()
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            return self.driver_model.create(data)
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            return self.driver_model.update(driver_id, data)
        elif cherrypy.request.method == 'DELETE':
            return self.driver_model.delete(driver_id)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def warehouses(self, warehouse_id=None):
        if cherrypy.request.method == 'GET':
            if warehouse_id:
                return self.warehouse_model.get(warehouse_id)
            return self.warehouse_model.list()
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            return self.warehouse_model.create(data)
        elif cherrypy.request.method == 'PUT':
            data = cherrypy.request.json
            return self.warehouse_model.update(warehouse_id, data)
        elif cherrypy.request.method == 'DELETE':
            return self.warehouse_model.delete(warehouse_id)
    #@cherrypy.expose  # This makes the method accessible via HTTP
    #@cherrypy.tools.json_out()  # This tells CherryPy to return the output as JSON
    #def index(self):
       #  return {"message": "Welcome to the Catalog Service API"}
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def feedback(self):
        if cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            driver_id = data.get('driver_id')
            warehouse_id = data.get('warehouse_id')
            self.feedback_model.create(data)
            if driver_id:
                self.driver_model.update_reputation(driver_id)
            if warehouse_id:
                self.warehouse_model.update_reputation(warehouse_id)
            return {'status': 'success'}
        elif cherrypy.request.method == 'GET':
            driver_id = cherrypy.request.params.get('driver_id')
            warehouse_id = cherrypy.request.params.get('warehouse_id')
            if driver_id:
                return self.feedback_model.list_for_driver(driver_id)
            if warehouse_id:
                return self.feedback_model.list_for_warehouse(warehouse_id)

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8083})
    cherrypy.quickstart(CatalogService(), '/')
