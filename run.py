import subprocess

def run_services():
    services = [
        "app/catalog_service/catalog.py",
        "app/reputation_service/reputation.py",
        "app/simulation_service/simulation.py",
        "app/web_app/web.py",
        "telegram_bot/bot.py"
    ]
    
    processes = []
    for service in services:
        processes.append(subprocess.Popen(["python", service]))
    
    for process in processes:
        process.wait()

if __name__ == "__main__":
    run_services()
