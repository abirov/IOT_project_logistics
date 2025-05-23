import subprocess

def run_services():
    services = [
        "app/catalog_service/catalog2.py",
        "app\DB_service\influxservice.py",
        "telegram_bot/Bot.py",
        
        "app/reputation_service/reputation.py",

        "app\DB_service\mqtt_service.py",
        "app\simulation_service\Test_simulation.py",


        "app/web_app/web.py",
          
        
    ]
    
    processes = []
    for service in services:
        # Start each service in a separate process
        processes.append(subprocess.Popen(["python", service]))
    
    # Wait for all processes to complete
    for process in processes:
        process.wait()

if __name__ == "__main__":
    run_services()





















