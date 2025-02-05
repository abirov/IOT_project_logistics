
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Package Registration</title>
</head>
<body>
    <h1>Register a New Package</h1>
    <form id="packageForm" action="http://127.0.0.1:8081/packages/packages" method="post">
        Name: <input type="text" id="name" name="name" required><br>
        Weight: <input type="number" id="weight" name="weight" step="0.01" required><br>
        Length: <input type="number" id="length" name="length" step="0.01" required><br>
        Width: <input type="number" id="width" name="width" step="0.01" required><br>
        Height: <input type="number" id="height" name="height" step="0.01" required><br>
        Warehouse ID: <input type="text" id="warehouse_id" name="warehouse_id" required><br>
        Status: <select id="status" name="status">
            <option value="in warehouse">In Warehouse</option>
            <option value="en route">En Route</option>
            <option value="delivered">Delivered</option>
        </select><br>
        <button type="submit">Submit</button>
    </form>

    <script>
        document.getElementById('packageForm').onsubmit = function(event) {
            event.preventDefault();  // Prevent the default form submission
            const formData = {
                name: document.getElementById('name').value,
                weight: parseFloat(document.getElementById('weight').value),
                dimensions: {
                    length: parseFloat(document.getElementById('length').value),
                    width: parseFloat(document.getElementById('width').value),
                    height: parseFloat(document.getElementById('height').value)
                },
                warehouse_id: document.getElementById('warehouse_id').value,
                status: document.getElementById('status').value
            };

            fetch(this.action, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => alert('Package registered successfully!'))
            .catch(error => alert('Error registering package: ' + error));
        };
    </script>
</body>
</html>
=======
import cherrypy
from jinja2 import Environment, FileSystemLoader
import requests
import os


class WebApp:
    def __init__(self, catalog_url):
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
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def submit_feedback(self):
        try:
            input_data = cherrypy.request.json
            required_fields = ['score']
            for field in required_fields:
                if not input_data.get(field):
                    raise ValueError(f"{field} is required.")

            score = float(input_data['score'])
            feedback_data = {
                'driver_id': input_data.get('driver_id'),
                'warehouse_id': input_data.get('warehouse_id'),
                'score': score,
                'comments': input_data.get('comments')
            }

            response = requests.post(f"{self.catalog_url}/feedback", json=feedback_data)
            response.raise_for_status()
            return {'status': 'success', 'message': 'Feedback submitted successfully'}
        except ValueError as ve:
            cherrypy.response.status = 400
            return {'status': 'error', 'message': str(ve)}
        except Exception as e:
            cherrypy.log(f"Error submitting feedback: {e}", traceback=True)
            cherrypy.response.status = 500
            return {'status': 'error', 'message': 'Failed to submit feedback'}

    def _get_vehicles(self):
        try:
            response = requests.get(f"{self.catalog_url}/vehicles")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            cherrypy.log(f"Error fetching vehicles: {e}", traceback=True)
            return [{'id': 'error', 'name': 'Error fetching vehicles'}]

    def _get_logistics_points(self):
        try:
            response = requests.get(f"{self.catalog_url}/logistics_points")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            cherrypy.log(f"Error fetching logistics points: {e}", traceback=True)
            return [{'id': 'error', 'name': 'Error fetching logistics points'}]

<<<<<<< HEAD
if __name__ == 'main':
    catalog_url = 'http://localhost:8080'  # Change to localhost if running locally
<<<<<<< HEAD
=======

if __name__ == '__main__':
    catalog_url = os.getenv('CATALOG_URL', 'http://localhost:8080')
>>>>>>> origin/main
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
    cherrypy.quickstart(WebApp(catalog_url), '/')
=======
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
    
>>>>>>> origin/MHOSS1
