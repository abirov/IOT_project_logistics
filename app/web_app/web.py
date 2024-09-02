import cherrypy
from jinja2 import Environment, FileSystemLoader
import requests
import os

class WebApp:
    def __init__(self, catalog_url):
        # Use an absolute path to the templates directory
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
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
    @cherrypy.tools.json_in()  # Added to parse incoming JSON
    def submit_feedback(self):
        try:
            # Log the incoming request data
            input_data = cherrypy.request.json
            driver_id = input_data.get('driver_id')
            warehouse_id = input_data.get('warehouse_id')
            score = input_data.get('score')
            comments = input_data.get('comments')

            cherrypy.log(f"Received feedback data: driver_id={driver_id}, warehouse_id={warehouse_id}, score={score}, comments={comments}")

            if score is None:
                raise ValueError("Score is required and must be a valid number.")

            cherrypy.log("Converting score to float")
            score = float(score)  # This will raise an error if 'score' is None or invalid

            feedback_data = {
                'driver_id': driver_id,
                'warehouse_id': warehouse_id,
                'score': score,
                'comments': comments
            }

            cherrypy.log(f"Sending feedback data to catalog service: {feedback_data}")
            response = requests.post(f"{self.catalog_url}/feedback", json=feedback_data)
            response.raise_for_status()  # This will raise an error for 4xx/5xx responses
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

if __name__ == '__main__':
    catalog_url = 'http://localhost:8080'  # Change to localhost if running locally
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
    
    # Configuration for serving static files
    conf = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.path.dirname(__file__), 'static')
        }
    }

    # Start the CherryPy server with the configuration for static files
    cherrypy.quickstart(WebApp(catalog_url), '/', conf)