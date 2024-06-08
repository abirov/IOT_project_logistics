import subprocess

def start_catalog_service():
    subprocess.Popen(["python", "app/services/catalog_service.py"])

def start_web_app():
    subprocess.Popen(["python", "app/web/web_app.py"])

def start_vehicle_simulation():
    subprocess.Popen(["python", "app/simulations

