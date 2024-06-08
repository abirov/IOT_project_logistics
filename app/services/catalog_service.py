import cherrypy
from bson import ObjectId
from app.models.logistics_points import (create_logistics_point, get_logistics_point, update_logistics_point, delete_logistics_point, list_logistics_points)

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

# Similar classes for vehicles, drivers, and warehouses

