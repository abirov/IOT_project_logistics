import cherrypy
from jinja2 import Environment, FileSystemLoader
import requests
import os

class WebApp:
    def init(self, catalog_url):
        # Use an absolute path to the templates directory
        template_dir = os.path.join(os.path.dirname(file), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.catalog_url = catalog_url

    @cherrypy.expose
    def index(self):
        try:
            template = self.env.get_template('index.html')
            vehicles = self._get_vehicles()
            logistics_points = self._get_logistics_points()
            return template.render(vehicles=vehicles, logistics_points=logistics_points)
        except Exception as e:
            cherrypy.log(f"Error rendering index.html: {e}", traceback=True)
            return "Internal Server Error"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def submit_feedback(self, driver_id=None, warehouse_id=None, score=None, comments=None):
        try:
            feedback_data = {
                'driver_id': driver_id,
                'warehouse_id': warehouse_id,
                'score': float(score),
                'comments': comments
            }
            response = requests.post(f"{self.catalog_url}/feedback", json=feedback_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            cherrypy.log(f"Error submitting feedback: {e}", traceback=True)
            return {'status': 'error', 'message': 'Failed to submit feedback'}

    def _get_vehicles(self):
        try:
            response = requests.get(f"{self.catalog_url}/vehicles")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            cherrypy.log(f"Error fetching vehicles: {e}", traceback=True)
            return []

    def _get_logistics_points(self):
        try:
            response = requests.get(f"{self.catalog_url}/logistics_points")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            cherrypy.log(f"Error fetching logistics points: {e}", traceback=True)
            return []

if name == 'main':
    catalog_url = 'http://localhost:8080'  # Change to localhost if running locally
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
    
    # Configuration for serving static files (CHANGES MADE HERE)
    conf = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.dirname(file), 'static')
        }
    }

    # Start the CherryPy server with the configuration for static files (CHANGES MADE HERE)
    cherrypy.quickstart(WebApp(catalog_url), '/', conf)