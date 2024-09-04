
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
    def init(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['logistics_db']
        self.logistics_point_model = LogisticsPoint(self.db)
        self.vehicle_model = Vehicle(self.db)
        self.driver_model = Driver(self.db)
        self.warehouse_model = Warehouse(self.db)
        self.feedback_model = Feedback(self.db)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def drivers(self, driver_id=None,):
        if cherrypy.request.method == 'GET':
            # Handling login when username and password are provided
            username = cherrypy.request.params.get('username')
            password = cherrypy.request.params.get('password')
            cherrypy.log(f"username: {username}, password: {password}")
            if username and password:
                try:
                    # Query the database for the username and password
                    driver = self.driver_model.find_by_username_password(username, password)
                    
                    if driver:
                        return {'status': 'success', 'driver_id': driver['driver_id']}
                    else:
                        return {'status': 'error', 'message': 'Invalid username or password'}
                except Exception as e:
                    cherrypy.log(f"Error during driver login: {e}", traceback=True)
                    return {'status': 'error', 'message': str(e)}
            else:
                return {'status': 'error', 'message': 'Username and password are required'}
        
        elif cherrypy.request.method == 'POST':
            data = cherrypy.request.json
            
            ###### Handling driver creation (sign-up)
            if 'driver_id' in data and 'username' in data and 'password' in data:
                try:
                    # Extract the necessary fields
                    driver_id = data.get('driver_id')
                    username = data.get('username')
                    password = data.get('password')

                    # Simple validation
                    if not driver_id or not username or not password:
                        raise ValueError("Driver ID, Username, and Password are required.")

                    # Prepare the data to be inserted
                    driver_data = {
                        'driver_id': driver_id,
                        'username': username,
                        'password': password,
                        'reputation': 0  # Initial reputation score
                    }

                    # Insert the driver data into the database
                    self.driver_model.create(driver_data)
                    
                    return {'status': 'success', 'message': 'Driver registered successfully'}
                except Exception as e:
                    cherrypy.log(f"Error during driver signup: {e}", traceback=True)
                    return {'status': 'error', 'message': str(e)}

            # If no valid operation is detected, return an error
            return {'status': 'error', 'message': 'Invalid operation'}

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
if __name__ == 'main':
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8080})
    cherrypy.quickstart(CatalogService(), '/')