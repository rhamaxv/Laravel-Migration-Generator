import datetime
import os

def load_template(template_path):
    with open(template_path, 'r') as f:
        return f.read()

def create_output_folder(database_name):
    datetime_prefix = datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')
    
    base_folder = os.path.join('output', database_name)
    os.makedirs(base_folder, exist_ok=True)
    
    folder = os.path.join(base_folder, datetime_prefix)
    os.makedirs(folder, exist_ok=True)
    
    return folder, datetime_prefix