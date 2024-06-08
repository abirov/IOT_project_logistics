import subprocess

def start_catalog_service():
    subprocess.Popen(["python", "app/services/catalog_service.py"])

def start_web_app():
    subprocess.Popen(["python", "app/web/web_app.py"])

def start_vehicle_simulation():
    subprocess.Popen(["python", "app/simulations/vehicle_simulation.py"])

def start_telegram_bot():
    subprocess.Popen(["python", "telegram_bot/bot.py"])

def start_telegraf():
    subprocess.Popen(["telegraf", "--config", "config/telegraf.conf"])

if __name__ == '__main__':
    start_catalog_service()
    start_web_app()
    start_vehicle_simulation()
    start_telegram_bot()
    start_telegraf()
