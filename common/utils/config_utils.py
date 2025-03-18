import yaml
import os

def load_config(config_file='config/config.yaml'):
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config_path = os.path.join(project_root, config_file)
    
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config