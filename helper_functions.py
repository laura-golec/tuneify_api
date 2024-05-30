import json
from flask import send_file, make_response, Response, jsonify
import shutil
from keys import *

def validate_api_key(api_key):
    if not api_key or (api_key not in API_KEYS):
        return False
    return True

def cleanup_files():
    # Delete all files in temp directory
    for file_name in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    print("Temporary files deleted")

def find_file_or_directory(name):
    for root, dirs, files in os.walk(ROOT_DIR):
        if name in files:
            return os.path.join(root, name)
        elif name in dirs:
            dir_path = os.path.join(root, name)
            if not os.path.exists(TEMP_DIR):
                os.makedirs(TEMP_DIR)
            zip_path = os.path.join(TEMP_DIR, name)
            shutil.make_archive(zip_path, 'zip', dir_path)
            return zip_path + '.zip'
    return None


def create_folder_structure_json(start_path, root):
    result = []
    def loop(start_path):
        currDir = {}
        full_path = root + start_path
        if os.path.isdir(full_path):
            current_node = start_path.split('/')[-1]
            currDir[current_node] = [{"path": start_path}]
            print('HEREEEEEEE', current_node)
            for item in os.listdir(full_path):
                item_path = os.path.join(start_path, item)
                print('this is the path ', item_path)
                if os.path.isdir(root + item_path):
                    loop(item_path)
                else:
                    item_full = {"name": item, "path": item_path}
                    currDir[current_node].append(item_full)
                    
            if(currDir[current_node] != [{"path": start_path}]):
                result.append(currDir)             
                return currDir

    loop(start_path)
    print(type(result))
    print(result)    

    response = jsonify(result)
    return response