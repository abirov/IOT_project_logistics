import json
import os

def load_config(model_name, config_file='config.json'):
    path = os.path.join(os.path.dirname(__file__), config_file)
    with open(path, 'r') as f:
        config = json.load(f)
    return config.get(model_name)