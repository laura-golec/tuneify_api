import inspect
import json
from flask import send_file, make_response, Response, jsonify
import shutil
import requests
import os

from keys import *
from helper_functions import *
from settings import change_settings

def handle_query_search(request):
    try:
        query = request.args.get('q')
        response = requests.get(f'https://api.deezer.com/search/?q=\'{query}\'&limit=10&output=json')
        
        if response.status_code == 200:
            data = response.json()  # Extract JSON content from the response
            return jsonify(data), 200
        else:
            return {'Error': f"Failed to fetch data from Deezer API. Status code: {response.status_code}"}, 500
    except Exception as error:
        return {'Error': str(error)}, 500

def handle_query_ipod(request):
    try:
        query = request.args.get('ipod')
        return jsonify({'ipod': query}), 200
    except Exception as error:
            return {'Error': str(error)}

# Handler function for downloading a file
def handle_query_download(request):
    try:
        query = request.args.get('download')
        print(query)
        root = ROOT_DIR + '/' + request.args.get('api_key')
        path = find_file_or_directory(root + query)

        download = send_file(path, as_attachment=True)
        return download
    except Exception as error:
        return {'Error': str(error)}

def handle_query_url(request):
    try:
        query = request.args.get('url')
        os.system(f'rip url {query}')
        return jsonify({'Done': 'I swear'})
    except Exception as error:
        return {'Error': str(error)}

def handle_query_browse(request):
    try:
        query = request.args.get('q')
        root = ROOT_DIR + '/' + request.args.get('api_key')
        response = create_folder_structure_json(query, root)
        if response.status_code == 200:
            print('gorted')
            return response
        else:
            return {'Error': f"Found nothing in {query}"}, 500
    except Exception as error:
        return {'Error': str(error)}, 500
    
def handle_query_config(request):
    try:
        path = request.args.getlist('path')
        value = request.args.get('value')
        return change_settings(RIP_SETTINGS, path, value)
    except Exception as error:
        return {'Error': str(error)}

# Get the module object representing the current module
handlers = inspect.getmodule(inspect.currentframe())

# Define the handler mapping dictionary
handler_mapping = {}
for name, obj in inspect.getmembers(handlers):
    if inspect.isfunction(obj) and name.startswith('handle_query_'):
        param_name = name.replace('handle_query_', '')
        handler_mapping[param_name] = obj