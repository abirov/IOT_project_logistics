import cherrypy
import json
from bson import objectid

from models.driverRepository2 import DriverRepository
from models.PackageRepository2 import PackageRepository
from models.warehouseRepository2 import WarehouseRepository
from models.FeedbackRepository2 import FeedbackRepository

# from models.LogisticsPointRepository import LogisticsPoint    #not modified yet
# from models.vehicleRepository import Vehicle                  #not modified yet

#depolay server for driver
class driverServer:
    def __init__(self,config_file='config.json'):
        self.driver_repo = DriverRepository(config_file=config_file)
        # self.package_repo = PackageRepository(config_file=config_file)

    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if "drivers" in uri:
            # If no specific parameter is provided, list all drivers
            if len(params) == 0:
                drivers = self.driver_repo.list_all()
                return [driver.to_dict() for driver in drivers]
            # If a driver ID is provided, get the driver by ID
            elif "driver_id" in params:
                driver_id = params["driver_id"]
                driver = self.driver_repo.get_by_id(driver_id)
                return driver.to_dict() if driver else None
            # If a driver email is provided, get the driver by email
            elif "driver_email" in params:
                driver_email = params["driver_email"]
                driver = self.driver_repo.get_by_email(driver_email)
                return driver.to_dict() if driver else None
            
            # If a driver name is provided, get the driver by name
            elif "driver_name" in params:
                driver_name = params["driver_name"]
                driver = self.driver_repo.get_by_name(driver_name)
                return driver.to_dict() if driver else None
            # If a package ID is provided, get the driver by package ID
            elif "package_id" in params:
                package_id = params["package_id"]
                driver = self.driver_repo.get_driver_by_package_id(package_id)
                return driver.to_dict() if driver else None
            else:
                raise cherrypy.HTTPError(400, "Invalid GET request")
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
    exposed = True        
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        if "drivers" in uri:
            data = cherrypy.request.json
            driver_id = self.driver_repo.create(data)
            return {"driver_id": driver_id}
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, *uri, **params):
        if "drivers" in uri:
            data = cherrypy.request.json
            driver_id = params["driver_id"]
            print(driver_id)
            result = self.driver_repo.update(driver_id, data)
            return result
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_out()
    def DELETE(self, *uri, **params):
        if "drivers" in uri:
            driver_id = params["driver_id"]
            result = self.driver_repo.delete(driver_id)
            return result
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        

#depolay server for warehouse
class warehouseServer:
    def __init__(self,config_file='config.json'):
        self.warehouse_repo = WarehouseRepository(config_file=config_file)

    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if "warehouses" in uri:
            # If no specific parameter is provided, list all warehouses
            if len(params) == 0:
                warehouses = self.warehouse_repo.list_all()
                return [warehouse.to_dict() for warehouse in warehouses]
            # If a warehouse ID is provided, get the warehouse by ID
            elif "warehouse_id" in params:
                warehouse_id = params["warehouse_id"]
                warehouse = self.warehouse_repo.get_by_id(warehouse_id)
                return warehouse.to_dict() if warehouse else None
            # If a warehouse email is provided, get the warehouse by email
            elif "warehouse_email" in params:
                warehouse_email = params["warehouse_email"]
                warehouse = self.warehouse_repo.get_by_email(warehouse_email)
                return warehouse.to_dict() if warehouse else None
           
            # If a warehouse name is provided, get the warehouse by name
            elif "warehouse_name" in params:
                warehouse_name = params["warehouse_name"]
                warehouse = self.warehouse_repo.get_by_name(warehouse_name)
                return warehouse.to_dict() if warehouse else None
            else:
                raise cherrypy.HTTPError(400, "Invalid GET request")
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
    exposed = True        
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        if "warehouses" in uri:
            data = cherrypy.request.json
            warehouse_id = self.warehouse_repo.create(data)
            return {"warehouse_id": warehouse_id}
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, *uri, **params):
        if "warehouses" in uri:
            data = cherrypy.request.json
            warehouse_id = params["warehouse_id"]
            result = self.warehouse_repo.update(warehouse_id, data)
            return result
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_out()
    def DELETE(self, *uri, **params):
        if "warehouses" in uri:
            warehouse_id = params["warehouse_id"]
            result = self.warehouse_repo.delete(warehouse_id)
            return result
        else:     
            raise cherrypy.HTTPError(404, "Invalid URI")
        
#depolay server for package
class packageServer:
    def __init__(self, config_file='config.json'):
        self.package_repo = PackageRepository(config_file=config_file)

    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if "packages" in uri:
            if len(params) == 0:
                packages = self.package_repo.list_all()
                return [package.to_dict() for package in packages]
            elif "package_id" in params:
                package_id = params["package_id"]
                package = self.package_repo.get_by_id(package_id)
                return package.to_dict() if package else None
            elif "warehouse_id" in params:
                warehouse_id = params["warehouse_id"]
                packages = self.package_repo.get_by_warehouse_id(warehouse_id)
                return [package.to_dict() for package in packages] if packages else None
            elif "no_driver" in params:
                packages = self.package_repo.list_all_packages_without_driver()
                return [package.to_dict() for package in packages]

            # NEW: If a driver ID is provided, get the packages for that driver
            elif "driver_id" in params:
                driver_id = params["driver_id"]
                # You need a method in your repository: get_by_driver_id(driver_id)
                packages = self.package_repo.get_by_driver_id(driver_id)
                return [package.to_dict() for package in packages] if packages else []
        
            else:
                raise cherrypy.HTTPError(400, "Invalid GET request")
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")


    exposed = True        
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        if "packages" in uri:
            data = cherrypy.request.json
            package_id = self.package_repo.create(data)
            return {"package_id": package_id}
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, *uri, **params):
        if "packages" in uri:
            data = cherrypy.request.json
            package_id = params["package_id"]
            result = self.package_repo.update(package_id, data)
            return result
        elif "assign_driver" in uri:
            package_id = params["package_id"]
            driver_id = params["driver_id"]
            result = self.package_repo.assign_driver(package_id, driver_id)
            return result
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_out()
    def DELETE(self, *uri, **params):
        if "packages" in uri:
            package_id = params["package_id"]
            result = self.package_repo.delete(package_id)
            return result
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
class FeedbackServer: 
    def __init__(self, config_file='config.json'):
        self.feedback_repo = FeedbackRepository(config_file=config_file)

    exposed = True
    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if "feedbacks" in uri:
            # If no specific parameter is provided, list all feedbacks
            if len(params) == 0:
                feedbacks = self.feedback_repo.list_all()
                return [feedback.to_dict() for feedback in feedbacks]
            # If a feedback ID is provided, get the feedback by ID
            elif "feedback_id" in params:
                feedback_id = params["feedback_id"]
                feedback = self.feedback_repo.get_by_id(feedback_id)
                return feedback.to_dict() if feedback else None
            # If a package ID is provided, get the feedback by package ID
            elif "package_id" in params:
                package_ids = params.get("package_id")  # ✅ CORRECT
                if isinstance(package_ids, str):
                    package_ids = [package_ids]  # Convert single string to list
                feedback = self.feedback_repo.get_by_package_ids(package_ids)
                return [fb.to_dict() for fb in feedback] if feedback else []
            # If a driver ID is provided, get the feedback by driver ID
            elif "driver_id" in params:
                driver_id = params["driver_id"]
                feedback = self.feedback_repo.get_by_driver_id(driver_id)
                return feedback.to_dict() if feedback else None
            # If a warehouse ID is provided, get the feedback by warehouse ID
            elif "warehouse_id" in params:
                warehouse_id = params["warehouse_id"]
                feedback = self.feedback_repo.get_by_warehouse_id(warehouse_id)
                return feedback.to_dict() if feedback else None
            else:
                raise cherrypy.HTTPError(400, "Invalid GET request")
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):
        if "feedbacks" in uri:
            data = cherrypy.request.json
            feedback_id = self.feedback_repo.create(data)
            return {"feedback_id": feedback_id}
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, *uri, **params):
        if "feedbacks" in uri:
            data = cherrypy.request.json
            feedback_id = params["feedback_id"]
            result = self.feedback_repo.update(feedback_id, data)
            return result
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
    exposed = True
    @cherrypy.tools.json_out()
    def DELETE(self, *uri, **params):
        if "feedbacks" in uri:
            feedback_id = params["feedback_id"]
            result = self.feedback_repo.delete(feedback_id)
            return result
        else:
            raise cherrypy.HTTPError(404, "Invalid URI")
        
     


        

        

if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(driverServer(), '/drivers', conf)
    cherrypy.tree.mount(warehouseServer(), '/warehouses', conf)
    cherrypy.tree.mount(packageServer(), '/packages', conf)
    cherrypy.tree.mount(FeedbackServer(), '/feedbacks', conf)
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()
