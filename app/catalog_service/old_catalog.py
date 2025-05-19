import cherrypy
import json

from models.driverRepository import DriverRepository
from models.warehouseRepository import WarehouseRepository
from models.feedbackRepository import FeedbackRepository
from models.vehicleRepository import Vehicle
# from models.LogisticsPointRepository import LogisticsPoint
#from models.packageRepository import PackageRepository
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
        self.driver_repo = DriverRepository(config_file=config_file)
        self.warehouse_repo = WarehouseRepository(config_file=config_file)
        self.feedback_repo = FeedbackRepository(config_file=config_file)
        self.vehicle_repo = Vehicle(config_file=config_file)
        #self.logpoint_repo = LogisticsPoint(config_file=config_file)
        #self.package_repo = PackageRepository(config_file=config_file)

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

    def update_reputation_driver(self, driver_id, data):
        return self.feedback_repo.update(driver_id,data)

    def get_reputation_driver(self, driver_id):
        return self.feedback_repo.get_by_driver_id(driver_id)

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
        return self.feedback_repo.update(warehouse_id, new_average)

    def get_reputation_warehouse(self, warehouse_id):
        return self.feedback_repo.get_by_warehouse_id(warehouse_id)

    ## Feedback Functionality
    def create_feedback(self, data):
        return self.feedback_repo.create(data)

    def get_feedback_by_id(self, f_id):
        return self.feedback_repo.get_by_id(f_id)

    def update_feedback(self, feedback_id, data):
        return self.feedback_repo.update(feedback_id, data)

    def delete_feedback(self, feedback_id):
        return self.feedback_repo.delete(feedback_id)

    def get_by_rating(self, f_id):
        return self.feedback_repo.get_by_rating(f_id)

    def get_feedback_by_driver(self, driver_id):
        return self.feedback_repo.get_by_driver_id(driver_id)

    def get_feedback_by_warehouse(self, warehouse_id):
        return self.feedback_repo.get_by_warehouse_id(warehouse_id)


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

    # def create_logpoint(self, data):
    #    return self.logpoint_repo.create(data)
    # def get_logpoint_by_id(self, point_id):
    #    return self.logpoint_repo.get_by_id(point_id)
    # def get_logpoint_by_name(self, point_name):
    #    return self.logpoint_repo.get_by_name(point_name)
    # def update_logpoint(self, point_id, data):
    #    return self.logpoint_repo.update(point_id, data)
    # def delete_logpoint(self, point_id):
    #    return self.logpoint_repo.delete(point_id)
    # def list_all_logpoints(self):
    #    return self.logpoint_repo.list_all()
    
    #package functionality
    #def create_package(self, data, warehouse_id):
    #    return self.package_repo.create(data, warehouse_id)
    #
    # def get_package_by_id(self, package_id):
    #     return self.package_repo.get_by_id(package_id)
    #
    # def get_package_by_driver(self, driver_id):
    #     return self.package_repo.get_by_driver(driver_id)
    #
    # def get_package_without_driver(self):
    #     return self.package_repo.list_all_without_driver()
    #
    # def get_package_by_warehouse(self, warehouse_id):
    #     return self.package_repo.get_by_warehouse(warehouse_id)
    #
    # def update_package(self, package_id,data):
    #     return self.package_repo.update(package_id,data)
    #
    # def delete_package(self, package_id):
    #     return self.package_repo.delete(package_id)
    #
    # def list_all_packages(self):
    #     return self.package_repo.list_all()



    # CHERRYPY API LAYER

class DriverServer:
        def __init__(self):
            self.service = CatalogService()

        exposed = True

        @cherrypy.tools.json_out()
        @cherrypy.tools.json_out()
        def GET(self, *uri, **params):
            if 'drivers' in uri:
                if 'list_all' in uri:
                    return [d.to_dict() for d in self.service.list_all_drivers()]
                elif len(uri) == 3 and uri[2].isdigit():
                    driver_id = uri[2]
                    driver = self.service.get_driver_by_id(driver_id)
                    if driver:
                        return driver.to_dict()
                    else:
                        raise cherrypy.HTTPError(404, "Driver not found")
                elif 'driver_name' in params:
                    return self.service.get_driver_by_name(params['driver_name']).to_dict()
                elif 'driver_id' in params and 'reputation' in params:
                    return self.service.get_reputation_driver(params['driver_id']).to_dict()

            raise cherrypy.HTTPError(400, "Invalid GET request")

        @cherrypy.tools.json_in()
        @cherrypy.tools.json_out()
        def POST(self, *uri, **params):
            data = cherrypy.request.json
            if 'drivers' in uri:
                return {"driver_id": self.service.put_driver(data)}
            raise cherrypy.HTTPError(400, "Invalid POST request")

        @cherrypy.tools.json_in()
        @cherrypy.tools.json_out()
        def PUT(self, *uri, **params):
            data = cherrypy.request.json
            if 'drivers' in uri and 'driver_id' in params:
                return {"updated": self.service.update_driver(params['driver_id'], data)}
            elif 'drivers' in uri and 'reputation' in uri and 'driver_id' in params:
                return {"updated": self.service.update_reputation_driver(params['driver_id'], data)}
            raise cherrypy.HTTPError(400, "Invalid PUT request")

        @cherrypy.tools.json_out()
        def DELETE(self, *uri, **params):
            if 'drivers' in uri and 'driver_id' in params:
                return {"deleted": self.service.delete_driver(params['driver_id'])}
            raise cherrypy.HTTPError(400, "Invalid DELETE request")

class WarehouseServer:
        def __init__(self):
            self.service = CatalogService()

        exposed = True

        @cherrypy.tools.json_out()
        def GET(self, *uri, **params):
            if 'warehouse' in uri:
                if 'list_all' in uri:
                    return [d.to_dict() for d in self.service.list_all_warehouses()]
                elif 'warehouse_id' in params:
                    return self.service.get_warehouse_by_id(params['warehouse_id']).to_dict()
                elif 'warehouse_id' in params and 'reputation' in params:
                    return self.service.get_reputation_warehouse(params['warehouse_id']).to_dict()
            raise cherrypy.HTTPError(400, "Invalid GET request")

        @cherrypy.tools.json_in()
        @cherrypy.tools.json_out()
        def POST(self, *uri, **params):
            data = cherrypy.request.json
            if 'warehouse' in uri:
                return {"warehouse_id": self.service.create_warehouse(data)}
            raise cherrypy.HTTPError(400, "Invalid POST request")

        @cherrypy.tools.json_in()
        @cherrypy.tools.json_out()
        def PUT(self, *uri, **params):
            data = cherrypy.request.json
            if 'warehouse' in uri and 'warehouse_id' in params:
                return {"updated": self.service.update_warehouse(params['warehouse_id'], data)}
            raise cherrypy.HTTPError(400, "Invalid PUT request")

        @cherrypy.tools.json_out()
        def DELETE(self, *uri, **params):
            if 'warehouse' in uri and 'warehouse_id' in params:
                return {"deleted": self.service.delete_warehouse(params['warehouse_id'])}
            raise cherrypy.HTTPError(400, "Invalid DELETE request")

class VehicleServer:
        def __init__(self):
            self.service = CatalogService()

        exposed = True
        @cherrypy.tools.json_out()
        def GET(self, *uri, **params):
            if 'vehicle' in uri:
                if 'vehicle_id' in params:
                    return [d.to_dict() for d in self.service.get_vehicle_by_id(params['vehicle_id']).to_dict()]
                elif 'list_all' in params:
                    return self.service.list_all_vehicles().to_dict()
                else:
                    raise cherrypy.HTTPError(400, "Invalid GET request")

        @cherrypy.tools.json_in()
        @cherrypy.tools.json_out()
        def POST(self, *uri, **params):
            data = cherrypy.request.json
            if 'vehicle' in uri:
                return {"vehicle_id": self.service.create_vehicle(data)}
            else:
                raise cherrypy.HTTPError(400, "Invalid POST request")

        @cherrypy.tools.json_in()
        @cherrypy.tools.json_out()
        def PUT(self, *uri, **params):
            try:
                data = cherrypy.request.json
                if 'vehicle' in uri and 'vehicle_id' in params:
                    result = self.service.update_vehicle(params['vehicle_id'], data)
                    return {"updated": result}
                else:
                    raise cherrypy.HTTPError(400, "Invalid PUT request")
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Server Error: {str(e)}")

        @cherrypy.tools.json_out()
        def DELETE(self, *uri, **params):
            try:
                if 'vehicle' in uri and 'vehicle_id' in params:
                    result = self.service.delete_vehicle(params['vehicle_id'])
                    return {"deleted": result}
                else:
                    raise cherrypy.HTTPError(400, "Invalid DELETE request")
            except Exception as e:
                raise cherrypy.HTTPError(500, f"Server Error: {str(e)}")

class FeedbackServer:
    def __init__(self):
        self.service = CatalogService()

    exposed = True

    @cherrypy.tools.json_out()
    def GET(self, *uri, **params):
        if 'feedback' in uri:
            if 'driver_id' in params:
                feedbacks = self.service.get_feedback_by_driver(params['driver_id'])
                return [feedback.to_dict() for feedback in feedbacks] if feedbacks else []
            elif 'warehouse_id' in params:
                feedbacks = self.service.get_feedback_by_warehouse(params['warehouse_id'])
                return [feedback.to_dict() for feedback in feedbacks] if feedbacks else []
            elif 'feedback_id' in params:
                feedback = self.service.get_feedback_by_id(params['feedback_id'])
                return feedback.to_dict() if feedback else {}
        else:
            raise cherrypy.HTTPError(400, "Missing driver_id, warehouse_id, or feedback_id")
        raise cherrypy.HTTPError(400, "Invalid GET request")

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, *uri, **params):

        data = cherrypy.request.json
        if 'feedback' in uri:
            return {"feedback_id": self.service.create_feedback(data)}
        else:
            raise cherrypy.HTTPError(400, "Invalid POST request")

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PUT(self, *uri, **params):
        try:
            data = cherrypy.request.json
            if 'feedback' in uri and 'feedback_id' in params:
                result = self.service.update_feedback(params['feedback_id'], data)
                return {"updated": result}
            else:
                raise cherrypy.HTTPError(400, "Invalid PUT request")
        except Exception as e:
            raise cherrypy.HTTPError(500, f"Server Error: {str(e)}")

    @cherrypy.tools.json_out()
    def DELETE(self, *uri, **params):
        try:
            if 'feedback' in uri and 'feedback_id' in params:
                result = self.service.delete_feedback(params['feedback_id'])
                return {"deleted": result}
            else:
                raise cherrypy.HTTPError(400, "Invalid DELETE request")
        except Exception as e:
            raise cherrypy.HTTPError(500, f"Server Error: {str(e)}")

if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
        }
    }
    cherrypy.tree.mount(DriverServer(), '/drivers', conf)
    cherrypy.tree.mount(WarehouseServer(), '/warehouse', conf)
    cherrypy.tree.mount(VehicleServer(), '/vehicle', conf)
    cherrypy.tree.mount(FeedbackServer(), '/feedback', conf)
    cherrypy.config.update({'server.socket_port': 8081})
    cherrypy.engine.start()
    cherrypy.engine.block()
