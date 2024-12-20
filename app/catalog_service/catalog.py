# from models.LogisticsPointRepository import LogisticsPoint
import cherrypy
from models.vehicleRepository import Vehicle
from models.driverRepository import Driver
from models.warehouseRepository import Warehouse
from models.feedbackRepository import Feedback
from models.LogisticsPointRepository import LogisticsPoint
from models.packageRepository import Package
import json
from bson import ObjectId

#custom json encoder to handle ObjectId
class CustomJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# class CatalogService:
class CatalogService:

    def __init__(self, config_file='config.json'):
        self.driver_repo = Driver(config_file=config_file)
        self.warehouse_repo = Warehouse(config_file=config_file)
        self.feedback_repo = Feedback(config_file=config_file)
        self.vehicle_repo = Vehicle(config_file=config_file)
        self.logpoint_repo = LogisticsPoint(config_file=config_file)
        self.package_repo = Package(config_file=config_file)

    ##  DRIVER FUNCTIONALITY
    def get_driver_by_id(self, driver_id='str'):
        return self.driver_repo.get_by_id(driver_id)

    def get_driver_by_name(self, driver_name='str'):
        return self.driver_repo.get_by_name(driver_name)

    def put_driver(self, data):
        return self.driver_repo.create(data)

    def update_driver(self, driver_id, data):
        return self.driver_repo.update(driver_id, data)

    def delete_driver(self, driver_id):
        return self.driver_repo.delete(driver_id)

    def list_all_drivers(self):
        return self.driver_repo.list_all()

    def update_reputation_driver(self, driver_id, new_average):
        return self.driver_repo.update_reputation(driver_id, new_average)

    ## Warehouse Functionality
    def create_warehouse(self, data):
        return self.warehouse_repo.create(data)

    def get_warehouse_by_id(self, warehouse_id):
        return self.warehouse_repo.get_by_id(warehouse_id)

    def update_warehouse(self, warehouse_id, data):
        return self.warehouse_repo.update(warehouse_id, data)

    def delete_warehouse(self, warehouse_id):
        return self.warehouse_repo.delete(warehouse_id)

    def list_all_warehouses(self):
        return self.warehouse_repo.list_all()

    def update_reputation_warehouse(self, warehouse_id, new_average):
        return self.warehouse_repo.update_reputation(warehouse_id, new_average)

    ## Feedback Functionality
    def create_feedback(self, data):
        return self.feedback_repo.create(data)

    def get_feedback_by_id(self, f_id):
        return self.feedback_repo.get_by_object_id(f_id)

    def update_feedback(self, feedback_id, data):
        return self.feedback_repo.update(feedback_id, data)

    def delete_feedback(self, feedback_id):
        return self.feedback_repo.delete(feedback_id)

    def get_score(self, f_id):
        return self.feedback_repo.get_score(f_id)

    ## Vehicle functionality
    def create_vehicle(self, data):
        return self.vehicle_repo.create(data)

    def get_vehicle_by_id(self, vehicle_id):
        return self.vehicle_repo.get_by_id(vehicle_id)

    def update_vehicle(self, vehicle_id, data):
        return self.vehicle_repo.update(vehicle_id, data)

    def delete_vehicle(self, vehicle_id):
        return self.vehicle_repo.delete(vehicle_id)

    def list_all_vehicles(self):
        return self.vehicle_repo.list_all()
    
    ## Logistics Point functionality

    def create_logpoint(self, data):
        return self.logpoint_repo.create(data)
    def get_logpoint_by_id(self, point_id):
        return self.logpoint_repo.get_by_id(point_id)
    def get_logpoint_by_name(self, point_name):
        return self.logpoint_repo.get_by_name(point_name)
    def update_logpoint(self, point_id, data):
        return self.logpoint_repo.update(point_id, data)
    def delete_logpoint(self, point_id):
        return self.logpoint_repo.delete(point_id)
    def list_all_logpoints(self):
        return self.logpoint_repo.list_all()
    
    #package functionality
    def create_package(self, data, warehouse_id):
        return self.package_repo.create(data, warehouse_id)
    
    @cherrypy.tools.json_out(cls=CustomJsonEncoder)
    def get_package_by_id(self, package_id):
        return self.package_repo.get_by_id(package_id)
    
    def get_package_by_driver(self, driver_id):
        return self.package_repo.get_by_driver(driver_id)
    
    def get_package_without_driver(self):
        return self.package_repo.list_all_without_driver()
    
    def get_package_by_warehouse(self, warehouse_id):
        return self.package_repo.get_by_warehouse(warehouse_id)
    
    def update_package(self, package_id,data):
        return self.package_repo.update(package_id,data)
    
    def delete_package(self, package_id):
        return self.package_repo.delete(package_id)
    
    def list_all_packages(self):
        return self.package_repo.list_all()
    


    exposed=True
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):

        # if uri and uri[0] == 'driver':
        if len(uri)>0 and uri[0] == 'driver':

            # If no specific parameter is provided, list all drivers
            if not params:
                return self.list_all_drivers()
            
            # Check for the presence of specific query parameters
            driver_id = params.get('driver_id')
            driver_name = params.get('driver_name')
            
            if driver_id:
                return self.get_driver_by_id(driver_id)
            elif driver_name:
                return self.get_driver_by_name(driver_name)
            else:
                # If neither driver_id nor driver_name is provided, return an error
                return {"error": "Please provide either driver_id or driver_name as a parameter"}
            

        elif len(uri)>0 and uri[0] == 'warehouse':
            # If no specific parameter is provided, list all warehouses
            if not params:
                return self.list_all_warehouses()
            
            # Check for the presence of specific query parameters
            warehouse_id = params.get('warehouse_id')
            
            if warehouse_id:
                return self.get_warehouse_by_id(warehouse_id)
            else:
                # If neither warehouse_id is provided, return an error
                return {"error": "Please provide warehouse_id as a parameter"}
            
        elif len(uri)>0 and uri[0] == 'feedback':

            # If no specific parameter is provided, list all feedbacks
            if not params:
                return self.feedback_repo.list_all()
            
            # Check for the presence of specific query parameters
            feedback_id = params.get('feedback_id')
            
            if feedback_id:
                return self.get_feedback_by_id(feedback_id)
            else:
                # If neither feedback_id is provided, return an error
                return {"error": "Please provide feedback_id as a parameter"}
        elif len(uri)>0 and uri[0] == 'vehicle':

            # If no specific parameter is provided, list all vehicles
            if not params:
                return self.list_all_vehicles()
            
            # Check for the presence of specific query parameters
            vehicle_id = params.get('vehicle_id')
            
            if vehicle_id:
                return self.get_vehicle_by_id(vehicle_id)
            else:
                # If neither vehicle_id is provided, return an error
                return {"error": "Please provide vehicle_id as a parameter"}
            
        elif len(uri)>0 and uri[0] == 'logpoint':

            # If no specific parameter is provided, list all logistics points
            if not params:
                return self.list_all_logpoints()
            
            # Check for the presence of specific query parameters
            point_id = params.get('point_id')
            point_name = params.get('point_name')
            
            if point_id:
                return self.get_logpoint_by_id(point_id)
            elif point_name:
                return self.get_logpoint_by_name(point_name)
            else:
                # If neither point_id nor point_name is provided, return an error
                return {"error": "Please provide either point_id or point_name as a parameter"}
        elif len(uri)>0 and uri[0] == 'package':

            # If no specific parameter is provided, list all packages
            if not params:
                x = self.package_repo.list_all()
                return json.dumps(x, cls=CustomJsonEncoder)
            
            # Check for the presence of specific query parameters

            package_id = params.get('package_id')
            driver_id = params.get('driver_id')
            warehouse_id = params.get('warehouse_id')
            no_driver = True
            
            if package_id:
                x = self.package_repo.get_by_id(package_id)
                return json.dumps(x, cls=CustomJsonEncoder)
            elif driver_id:
                x = self.package_repo.get_by_driver(driver_id)
                return json.dumps(x, cls=CustomJsonEncoder)
            elif warehouse_id:
                x = self.package_repo.get_by_warehouse(warehouse_id)
                return json.dumps(x, cls=CustomJsonEncoder) 
            elif no_driver:
                x = self.package_repo.list_all_without_driver()
                return json.dumps(x, cls=CustomJsonEncoder)
            else:
                # If neither package_id nor driver_id nor warehouse_id is provided, return an error
                return {"error": "Please provide either package_id or driver_id or warehouse_id as a parameter"}
                
    exposed=True
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self, *uri, **params):
        if len(uri)>0 and uri[0] == 'driver':
            data = cherrypy.request.json
            return self.put_driver(data)
        
        elif len(uri)>0 and uri[0] == 'warehouse':
            data = cherrypy.request.json
            return self.create_warehouse(data)
        
        elif len(uri)>0 and uri[0] == 'feedback':
            data = cherrypy.request.json
            return self.create_feedback(data)
        
        elif len(uri)>0 and uri[0] == 'vehicle':
            data = cherrypy.request.json
            return self.create_vehicle(data)
        
        elif len(uri)>0 and uri[0] == 'logpoint':
            data = cherrypy.request.json
            return self.create_logpoint(data)
        
        elif len(uri)>0 and uri[0] == 'package':
            data = cherrypy.request.json
            warehouse_id = params.get('warehouse_id')
            return self.create_package(data,warehouse_id)
        
    exposed=True
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def DELETE(self, *uri, **params):
        if len(uri)>0 and uri[0] == 'driver':
            driver_id = params.get('driver_id')
            return self.delete_driver(driver_id)
        
        elif len(uri)>0 and uri[0] == 'warehouse':
            warehouse_id = params.get('warehouse_id')
            return self.delete_warehouse(warehouse_id)
        
        elif len(uri)>0 and uri[0] == 'feedback':
            feedback_id = params.get('feedback_id')
            return self.delete_feedback(feedback_id)
        
        elif len(uri)>0 and uri[0] == 'vehicle':
            vehicle_id = params.get('vehicle_id')
            return self.delete_vehicle(vehicle_id)
        
        elif len(uri)>0 and uri[0] == 'logpoint':
            point_id = params.get('point_id')
            return self.delete_logpoint(point_id)
        
        elif len(uri)>0 and uri[0] == 'package':
            package_id = params.get('package_id')
            return self.delete_package(package_id)
        
    exposed=True
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def PUT(self, *uri, **params):
        if len(uri)>0 and uri[0] == 'driver':
            driver_id = params.get('driver_id')
            data = cherrypy.request.json
            return self.update_driver(driver_id, data)
        
        elif len(uri)>0 and uri[0] == 'warehouse':
            warehouse_id = params.get('warehouse_id')
            data = cherrypy.request.json
            return self.update_warehouse(warehouse_id, data)
        
        elif len(uri)>0 and uri[0] == 'feedback':
            feedback_id = params.get('feedback_id')
            data = cherrypy.request.json
            return self.update_feedback(feedback_id, data)
        
        elif len(uri)>0 and uri[0] == 'vehicle':
            vehicle_id = params.get('vehicle_id')
            data = cherrypy.request.json
            return self.update_vehicle(vehicle_id, data)
        
        elif len(uri)>0 and uri[0] == 'logpoint':
            point_id = params.get('point_id')
            data = cherrypy.request.json
            return self.update_logpoint(point_id, data)
        
        elif len(uri)>0 and uri[0] == 'package':
            package_id = params.get('package_id')
            data = cherrypy.request.json
            return self.update_package(package_id, data)




if __name__ == '__main__':
    # cherrypy_cors.install()
    
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(CatalogService(), '/' ,conf)
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()
