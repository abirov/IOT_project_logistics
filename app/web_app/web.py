import cherrypy
from jinja2 import Environment, FileSystemLoader
import requests

class WebApp:
    def __init__(self, catalog_url):
        self.catalog_url = catalog_url
        self.env = Environment(loader=FileSystemLoader('app/web_app/templates'))

    @cherrypy.expose
    def index(self):
        template = self.env.get_template('index.html')
        vehicles = self._get_vehicles()
        logistics_points = self._get_logistics_points()
        return template.render(vehicles=vehicles, logistics_points=logistics_points)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def submit_feedback(self, driver_id=None, warehouse_id=None, score=None, comments=None):
        feedback_data = {
            'driver_id': driver_id,
            'warehouse_id': warehouse_id,
            'score': float(score),
            'comments': comments
        }
        response = requests.post(f"{self.catalog_url}/feedback", json=feedback_data)
        return response.json()

    def _get_vehicles(self):
        response = requests.get(f"{self.catalog_url}/vehicles")
        return response.json()

    def _get_logistics_points(self):
        response = requests.get(f"{self.catalog_url}/logistics_points")
        return response.json()

if __name__ == '__main__':
    catalog_url = 'http://catalog_service:8080'
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
    cherrypy.quickstart(WebApp(catalog_url), '/')
