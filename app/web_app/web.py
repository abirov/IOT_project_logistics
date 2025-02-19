import cherrypy
from jinja2 import Environment, FileSystemLoader
import requests
import os
from datetime import datetime
import json
class WebApp:
    def __init__(self, catalog_url):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.env = Environment(loader=FileSystemLoader(template_dir))
        catalog_url = os.getenv('CATALOG_URL', 'http://127.0.0.1:8080')  #  localhost
        self.catalog_url = catalog_url

    @cherrypy.expose
    def index(self):
        """Landing Page: Choose Driver or Warehouse"""
        try:
            template = self.env.get_template('index.html')
            return template.render()
        except Exception as e:
            cherrypy.log(f"Error rendering index.html: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    def driver_options(self):
        """Driver Options: Sign-In or Login"""
        try:
            template = self.env.get_template('driver_options.html')
            return template.render()
        except Exception as e:
            cherrypy.log(f"Error rendering driver_options.html: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    def signin(self):
        """Driver Sign-In Page"""
        try:
            template = self.env.get_template('driver_signin.html')
            return template.render()
        except Exception as e:
            cherrypy.log(f"Error rendering driver_signin.html: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    def submit_signin(self, name, email, phone, address, license_number):
        """Submit Driver Sign-In Data to Catalog"""
        try:
            data = {
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "license_number": license_number,
            }
            response = requests.post("http://127.0.0.1:8080/drivers/drivers", json=data)
            response.raise_for_status()
            result = response.json()
            driver_id = result.get("driver_id")
            return f"<h1>Driver signed up successfully!</h1><p>Your Driver ID is: {driver_id}</p>"
        except Exception as e:
            cherrypy.log(f"Error submitting sign-in: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to sign up driver")

    @cherrypy.expose
    def login(self):
        """Driver Login Page"""
        try:
            template = self.env.get_template('driver_login.html')
            return template.render()
        except Exception as e:
            cherrypy.log(f"Error rendering driver_login.html: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    def authenticate(self, driver_id):
        """Authenticate Driver by ID"""
        try:
            url = "http://127.0.0.1:8080/drivers/drivers"
            cherrypy.log(f"Authenticating driver_id: {driver_id}")
            response = requests.get(url, params={"driver_id": driver_id})
            response.raise_for_status()
            driver = response.json()
            cherrypy.log(f"Driver data from catalog: {driver}")

            if driver and driver.get("_id") == driver_id:
                cherrypy.log(f"Driver found: {driver}")
                redirect_url = f"/dashboard?driver_id={driver_id}"
                cherrypy.response.headers["Location"] = redirect_url
                cherrypy.response.status = 303
                return f'<html><body>Redirecting to <a href="{redirect_url}">dashboard</a>.</body></html>'
       
            else:
                cherrypy.log("Driver not found.")
                return "<h1>Driver not found. Please try again.</h1>"
            
        except Exception as e:
            cherrypy.log(f"Error authenticating driver: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to authenticate driver")

    


    @cherrypy.expose
    def dashboard(self, driver_id):
        """Driver Dashboard"""
        try:
            # driver details
            driver_url = "http://127.0.0.1:8080/drivers/drivers"
            driver_response = requests.get(driver_url, params={"driver_id": driver_id})
            driver_response.raise_for_status()
            driver = driver_response.json()
            cherrypy.log(f"Driver data: {driver}")

            # feedbacks for the driver
            feedback_url = "http://127.0.0.1:8080/feedbacks/feedbacks"
            feedback_response = requests.get(feedback_url, params={"driver_id": driver_id})
            
            if feedback_response.status_code == 200:
                cherrypy.log(f"Feedbacks response: {feedback_response.text}")
                feedbacks = feedback_response.json()
                # If feedbacks is null set it to an empty list
                if feedbacks is None:
                    feedbacks = []

                #  feedbacks is a list?
                if isinstance(feedbacks, str):
                    try:
                        feedbacks = json.loads(feedbacks)  # parse
                    except json.JSONDecodeError:
                        cherrypy.log("Failed to parse feedbacks as JSON")
                        feedbacks = []
                
                if isinstance(feedbacks, dict):
                    feedbacks = [feedbacks]  # Convert single feedback to a list 
                
                
                feedback_list = []
                for f in feedbacks:
                    if isinstance(f, dict):  # f is a dictionary?
                        feedback = {
                            "package_id": str(f.get("package_id", "Unknown package")),
                            "score": float(f.get("score", 0)), 
                            "comment": str(f.get("comment", "No comments")),
                            "weight": float(f.get("weight", 0)),  
                            "warehouse_id": str(f.get("warehouse_id", "Unknown warehouse")),
                            "timestamp": str(f.get("timestamp", "Unknown time"))
                        }
                        feedback_list.append(feedback)

                cherrypy.log(f"Processed feedback list: {feedback_list}")
            else:
                cherrypy.log(f"Failed to retrieve feedbacks: {feedback_response.status_code}")
                feedback_list = []

            # Fetch available packages
            available_package_url = "http://127.0.0.1:8080/packages/packages?no_driver=true"
            available_response = requests.get(available_package_url)
            available_response.raise_for_status()
            available_packages = available_response.json() or []

            # Fetch selected packages
            try:
                selected_package_url = f"http://127.0.0.1:8080/packages/packages?driver_id={driver_id}"
                selected_response = requests.get(selected_package_url)
                selected_response.raise_for_status()
                selected_packages = selected_response.json() or []
            except requests.exceptions.RequestException as e:
                cherrypy.log(f"Error fetching selected packages: {e}")
                selected_packages = []

            
            template = self.env.get_template('driver_dashboard.html')
            return template.render(
                driver=driver,
                feedbacks=feedback_list,
                available_packages=available_packages,
                selected_packages=selected_packages
            )

        except requests.exceptions.RequestException as req_err:
            cherrypy.log(f"HTTP error when fetching data: {req_err}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to fetch data from the service")
        except Exception as e:
            cherrypy.log(f"Unexpected error rendering dashboard: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to load dashboard")
        
    @cherrypy.expose
    def select_package(self, driver_id, package_id):
        """Handle the package selection and update the driver_id via PUT request"""
        try:
            # Prepare the payload for  PUT 
            payload = {"driver_id": driver_id}

            # update package with  driver_id
            select_package_url = f"http://127.0.0.1:8080/packages/packages?package_id={package_id}"
            response = requests.put(select_package_url, json=payload)
            response.raise_for_status()

            cherrypy.log(f"Package {package_id} updated with driver {driver_id}")
            return self.dashboard(driver_id)  # go to dashboard 

        except requests.exceptions.RequestException as e:
            cherrypy.log(f"Error selecting package {package_id}: {e}")
            raise cherrypy.HTTPError(500, "Failed to select package")
        except Exception as e:
            cherrypy.log(f"Unexpected error: {e}")
            raise cherrypy.HTTPError(500, "Unexpected error selecting package")
     
    @cherrypy.expose
    def mark_delivered(self, driver_id, package_id):
        
       
            payload = {"status": "delivered"}
            url = f"http://127.0.0.1:8080/packages/packages?package_id={package_id}"

            # update the package's status
            response = requests.put(url, json=payload)
            response.raise_for_status()

            cherrypy.log(f"Package {package_id} marked as delivered by driver {driver_id}")
            # no redirect
            return f"well done you delivered Package {package_id} successfully!"
    

     

    @cherrypy.expose
    def edit_profile(self, driver_id):
        
        try:
            #  current driver data  fetching
            response = requests.get("http://127.0.0.1:8080/drivers/drivers", params={"driver_id": driver_id})
            response.raise_for_status()
            driver_data = response.json()

            # HTML to edit driver
            return f"""
            <html>
            <head><title>Edit Driver Profile</title></head>
            <body>
                <h2>Edit Profile for: {driver_data['name']}</h2>
                <form action="/submit_edit_profile" method="post">
                    <input type="hidden" name="driver_id" value="{driver_id}">
                    Name: <input type="text" name="name" value="{driver_data['name']}"><br>
                    Email: <input type="text" name="email" value="{driver_data['email']}"><br>
                    Phone: <input type="text" name="phone" value="{driver_data['phone']}"><br>
                    Address: <input type="text" name="address" value="{driver_data['address']}"><br>
                    License Number: <input type="text" name="license_number" value="{driver_data['license_number']}"><br>
                    <button type="submit">Save Changes</button>
                </form>
            </body>
            </html>
            """
        except Exception as e:
            cherrypy.log(f"Error displaying edit form: {e}")
            raise cherrypy.HTTPError(500, "Failed to display edit form")

    @cherrypy.expose
    def submit_edit_profile(self, driver_id, name, email, phone, address, license_number):
        """
        Submits the edited driver profile via PUT method to update the driver details.
        """
        try:
            data = {
                "name": name,
                "email": email,
                "phone": phone,
                "address": address,
                "license_number": license_number
            }
            
            url = f"http://127.0.0.1:8080/drivers/drivers?driver_id={driver_id}"
            response = requests.put(url, json=data)
            response.raise_for_status()

            return f"""
            <html><body>
                <h3>Profile Updated Successfully!</h3>
                <a href="/dashboard?driver_id={driver_id}">Back to Dashboard</a>
            </body></html>
            """
        except requests.exceptions.RequestException as e:
            cherrypy.log(f"Error updating driver profile: {e}")
            raise cherrypy.HTTPError(500, "Failed to update driver profile")

    @cherrypy.expose
    def delete_profile(self, driver_id):
        
        try:
            
            url = f"http://127.0.0.1:8080/drivers/drivers?driver_id={driver_id}"
            response = requests.delete(url)
            response.raise_for_status()

            return f"""
            <html><body>
                <h3>Driver {driver_id} Profile Deleted.</h3>
                <p>All data for this driver has been removed.</p>
                <a href="/driver_options">Return to Driver Options</a>
            </body></html>
            """
        except requests.exceptions.RequestException as e:
            cherrypy.log(f"Error deleting driver profile: {e}")
            raise cherrypy.HTTPError(500, "Failed to delete driver profile")
        except Exception as e:
            cherrypy.log(f"Unexpected error: {e}")
            raise cherrypy.HTTPError(500, "Unexpected error deleting driver profile")



     #####warehouse

    @cherrypy.expose
    def warehouse_options(self):
        """Warehouse Options: Sign-In or Login"""
        try:
            template = self.env.get_template('warehouse_options.html')
            return template.render()
        except Exception as e:
            cherrypy.log(f"Error rendering warehouse_options.html: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    def warehouse_signin(self):
        """Warehouse Sign-In Page"""
        try:
            template = self.env.get_template('warehouse_signin.html')
            return template.render()
        except Exception as e:
            cherrypy.log(f"Error rendering warehouse_signin.html: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    def submit_warehouse_signin(self, name, street, city, state, zip, phone, email):
        """Submit Warehouse Sign-In Data"""
        try:
            data = {
                "name": name,
                "address": {"street": street, "city": city, "state": state, "zip": zip},
                "phone": phone,
                "email": email,
            }
            
            response = requests.post("http://127.0.0.1:8080/warehouses/warehouses", json=data)
            response.raise_for_status()
            result = response.json()
            warehouse_id = result.get("warehouse_id")
            return f"<h1>Warehouse signed up successfully!</h1><p>Your Warehouse ID is: {warehouse_id}</p>"
        except Exception as e:
            cherrypy.log(f"Error submitting warehouse sign-in: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to sign up warehouse")

    @cherrypy.expose
    def warehouse_login(self):
        """Warehouse Login Page"""
        try:
            template = self.env.get_template('warehouse_login.html')
            return template.render()
        except Exception as e:
            cherrypy.log(f"Error rendering warehouse_login.html: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Internal Server Error")

    @cherrypy.expose
    def warehouse_authenticate(self, warehouse_id):
        """Authenticate Warehouse by ID"""
        try:
            url = "http://127.0.0.1:8080/warehouses/warehouses"
            cherrypy.log(f"Authenticating warehouse_id: {warehouse_id}")
            response = requests.get(url, params={"warehouse_id": warehouse_id})
            response.raise_for_status()
            warehouse = response.json()
            cherrypy.log(f"Warehouse data from catalog: {warehouse}")

            if warehouse and warehouse.get("_id") == warehouse_id:
                cherrypy.log(f"Warehouse found: {warehouse}")
                redirect_url = f"/warehouse_dashboard?warehouse_id={warehouse_id}"
                cherrypy.response.headers["Location"] = redirect_url
                cherrypy.response.status = 303
                return f'<html><body>Redirecting to <a href="{redirect_url}">dashboard</a>.</body></html>'
            else:
                cherrypy.log("Warehouse not found.")
                return "<h1>Warehouse not found. Please try again.</h1>"
        except Exception as e:
            cherrypy.log(f"Error authenticating warehouse: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to authenticate warehouse")

   

    @cherrypy.expose
    def warehouse_dashboard(self, warehouse_id):
        """Warehouse Dashboard"""
        try:
            #  warehouse details
            warehouse_url = f"http://127.0.0.1:8080/warehouses/warehouses"
            warehouse_response = requests.get(warehouse_url, params={"warehouse_id": warehouse_id})
            warehouse_response.raise_for_status()
            warehouse = warehouse_response.json()
            cherrypy.log(f"Warehouse data: {warehouse}")

            #  package history for the warehouse
            packages_url = f"http://127.0.0.1:8080/packages/packages"
            packages_response = requests.get(packages_url, params={"warehouse_id": warehouse_id})
            packages_response.raise_for_status()
            packages = packages_response.json()
            cherrypy.log(f"Package history data: {packages}")

            template = self.env.get_template('warehouse_dashboard.html')
            return template.render(
                name=warehouse["name"],
                address=warehouse["address"],
                phone=warehouse["phone"],
                email=warehouse["email"],
                reputation=warehouse["reputation"],
                packages=packages,
                warehouse_id=warehouse_id
            )
        except Exception as e:
            cherrypy.log(f"Error rendering warehouse dashboard: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to load warehouse dashboard")
    
    @cherrypy.expose
    def edit_warehouse(self, warehouse_id):
        """
         displays a form to edit it
        """
        try:
            # current warehouse data from catalog
            warehouse_url = "http://127.0.0.1:8080/warehouses/warehouses"
            response = requests.get(warehouse_url, params={"warehouse_id": warehouse_id})
            response.raise_for_status()
            warehouse_data = response.json()  # {"_id": ..., "name": ..., "address": {...}, ...}

            
            return f"""
            <html>
            <head><title>Edit Warehouse</title></head>
            <body>
                <h2>Edit Warehouse: {warehouse_data['name']}</h2>
                <form action="/submit_edit_warehouse" method="post">
                    <input type="hidden" name="warehouse_id" value="{warehouse_id}">

                    Name: <input type="text" name="name" value="{warehouse_data['name']}"><br>
                    Street: <input type="text" name="street" value="{warehouse_data['address']['street']}"><br>
                    City: <input type="text" name="city" value="{warehouse_data['address']['city']}"><br>
                    State: <input type="text" name="state" value="{warehouse_data['address']['state']}"><br>
                    Zip: <input type="text" name="zip" value="{warehouse_data['address']['zip']}"><br>
                    Phone: <input type="text" name="phone" value="{warehouse_data['phone']}"><br>
                    Email: <input type="text" name="email" value="{warehouse_data['email']}"><br>

                    <button type="submit">Save Changes</button>
                </form>
            </body>
            </html>
            """
        except Exception as e:
            cherrypy.log(f"Error displaying edit form for warehouse {warehouse_id}: {e}")
            raise cherrypy.HTTPError(500, "Failed to display edit form")

    @cherrypy.expose
    def submit_edit_warehouse(self, warehouse_id, name, street, city, state, zip, phone, email):
        """
        PUT method to update the warehouse details 
        """
        try:
            # updated warehouse data
            data = {
                "name": name,
                "address": {
                    "street": street,
                    "city": city,
                    "state": state,
                    "zip": zip
                },
                "phone": phone,
                "email": email
            }

           
            url = f"http://127.0.0.1:8080/warehouses/warehouses?warehouse_id={warehouse_id}"
            response = requests.put(url, json=data)
            response.raise_for_status()

            return f"""
            <html><body>
                <h3>Warehouse {warehouse_id} Updated Successfully!</h3>
                <a href="/warehouse_dashboard?warehouse_id={warehouse_id}">Back to Warehouse Dashboard</a>
            </body></html>
            """
        except requests.exceptions.RequestException as e:
            cherrypy.log(f"Error updating warehouse {warehouse_id}: {e}")
            raise cherrypy.HTTPError(500, "Failed to update warehouse")
        except Exception as e:
            cherrypy.log(f"Unexpected error: {e}")
            raise cherrypy.HTTPError(500, "Unexpected error updating warehouse")

    @cherrypy.expose
    def delete_warehouse(self, warehouse_id):
        """
        Deletes the warehouse profile 
        """
        try:
            
            url = f"http://127.0.0.1:8080/warehouses/warehouses?warehouse_id={warehouse_id}"
            response = requests.delete(url)
            response.raise_for_status()

            return f"""
            <html><body>
                <h3>Warehouse {warehouse_id} Profile Deleted.</h3>
                <p>All data related to this warehouse was removed .</p>
                <a href="/warehouse_options">Return to Warehouse Options</a>
            </body></html>
            """
        except requests.exceptions.RequestException as e:
            cherrypy.log(f"Error deleting warehouse {warehouse_id}: {e}")
            raise cherrypy.HTTPError(500, "Failed to delete warehouse")
        except Exception as e:
            cherrypy.log(f"Unexpected error: {e}")
            raise cherrypy.HTTPError(500, "Unexpected error deleting warehouse")
    @cherrypy.expose
    def register_package(self, warehouse_id, package_name, source, destination, weight, price, dimensions, delivery_address):
        """Register a new package"""
        try:
            # Log received input for debugging
            cherrypy.log(f"Received data: warehouse_id={warehouse_id}, package_name={package_name}, "
                        f"source={source}, destination={destination}, weight={weight}, price={price}, dimensions={dimensions}, delivery_address={delivery_address}")

            # dimensions (format: LxWxH)
            try:
                length, width, height = map(float, dimensions.split('x'))
                package_dimensions = {"length": length, "width": width, "height": height}
            except ValueError:
                raise ValueError("Invalid dimensions format. Use 'LxWxH'.")

            # Prepare package data
            package_data = {
                "name": package_name,
                "warehouse_id": warehouse_id,
                "source": source,
                "destination": destination,
                "weight": float(weight),  
                "price": float(price),
                "dimensions": package_dimensions,
                "delivery_address": delivery_address,  
                "status": "in warehouse",
            }

            # Log the prepared package data
            cherrypy.log(f"Prepared package data: {package_data}")

            # Send the POST request
            response = requests.post(f"http://127.0.0.1:8080/packages/packages", json=package_data)
            response.raise_for_status()

            return f"<h1>Package '{package_name}' registered successfully for Warehouse {warehouse_id}!</h1>"
        except ValueError as ve:
            cherrypy.log(f"Validation error: {ve}", traceback=True)
            raise cherrypy.HTTPError(400, f"Invalid input: {ve}")
        except Exception as e:
            cherrypy.log(f"Error registering package: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to register package")    
                
    @cherrypy.expose
    def register_feedback(self, package_id, driver_id, score, comment, weight, warehouse_id=None):
        """Register feedback for a driver"""
        try:
            # Prepare feedback data
            feedback_data = {
                "package_id": package_id,
                "driver_id": driver_id,
                "score": int(score),  
                "comment": comment,
                "weight": float(weight),  
                "warehouse_id": warehouse_id,  
                "timestamp": datetime.now().isoformat()  
            }

            # Log feedback data for debugging
            cherrypy.log(f"Feedback data being submitted: {feedback_data}")

            # Send the feedback 
            response = requests.post(f"http://127.0.0.1:8080/feedbacks/feedbacks", json=feedback_data)
            response.raise_for_status()


            return f"<h1>Feedback submitted successfully for Package {package_id}!</h1>"
        except requests.exceptions.RequestException as req_err:
            
            cherrypy.log(f"HTTP error when registering feedback: {req_err}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to communicate with the feedback service")
        except Exception as e:
            #  unexpected errors
            cherrypy.log(f"Unexpected error registering feedback: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "An unexpected error occurred while submitting feedback")

    @cherrypy.expose
    def search_package(self, package_id):
        """Search package by ID"""
        try:
            url = f"http://127.0.0.1:8080/packages"
            response = requests.get(url, params={"package_id": package_id})
            response.raise_for_status()
            package = response.json()
            template = self.env.get_template('warehouse_dashboard.html')
            return template.render(
                package=package
            )
        except Exception as e:
            cherrypy.log(f"Error searching package: {e}", traceback=True)
            raise cherrypy.HTTPError(500, "Failed to search package")





if __name__ == '__main__':
    catalog_url = os.getenv('CATALOG_URL', 'http://localhost:8080')
    cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': 8081})
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config = {
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(current_dir, 'static'),
        }
    }

    cherrypy.quickstart(WebApp(catalog_url), '/',config)
