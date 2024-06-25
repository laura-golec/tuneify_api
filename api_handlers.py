import inspect
import json
from flask import send_file, make_response, Response, jsonify
import shutil
import requests
import subprocess
import os
from app import app

from keys import *
from helper_functions import *
from settings import change_settings

def handle_query_search(request):
    try:
        query = request.args.get('q')
        localResponse = handle_query_find(request).json()
        response = requests.get(f'https://api.deezer.com/search/?q=\'{query}\'&limit=10&output=json')
        if response.status_code == 200:
            deezerData = response.json() if response.status_code == 200 else []
            return jsonify(data), 200
        else:
            return {'Error': f"Failed to fetch data from Deezer API. Status code: {response.status_code}"}, 500
    except Exception as error:
        return {'Error': str(error)}, 500
    
def handle_query_ipod(request):
    try:
        query = request.args.get('q')
        return jsonify({'ipod': query}), 200
    except Exception as error:
            return {'Error': str(error)}

# Handler function for downloading a file
def handle_query_download(request):
    try:
        path = handle_query_find(request)

        download = send_file(path, as_attachment=True)
        return download
    except Exception as error:
        return {'Error': str(error)}

def run_command(command, sudo=False):
    try:
        app.logger.info(f"Running command: {command}")

        if sudo:
            command = f"echo {SUDO_PASSWORD} | sudo -S -k {command}"

        # Start the command asynchronously
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env={'PATH': '/usr/bin:/bin'}
        )

        # Read output and errors continuously until the process completes
        stdout_lines = []
        stderr_lines = []
        while True:
            stdout = process.stdout.readline()
            stderr = process.stderr.readline()
            if stdout:
                stdout_lines.append(stdout.strip())
                app.logger.info(f"stdout: {stdout.strip()}")
            if stderr:
                stderr_lines.append(stderr.strip())
                app.logger.error(f"stderr: {stderr.strip()}")
            if process.poll() is not None:  # Check if the process has completed
                break

        # Capture remaining output
        remaining_stdout, remaining_stderr = process.communicate()
        if remaining_stdout:
            stdout_lines.append(remaining_stdout.strip())
            app.logger.info(f"Remaining stdout: {remaining_stdout.strip()}")
        if remaining_stderr:
            stderr_lines.append(remaining_stderr.strip())
            app.logger.error(f"Remaining stderr: {remaining_stderr.strip()}")

        # Check return code
        returncode = process.returncode
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, command, "\n".join(stderr_lines))

        return "\n".join(stdout_lines).strip(), None

    except subprocess.CalledProcessError as error:
        app.logger.error(f"Command '{command}' failed with return code {error.returncode}: {error.stderr}")
        return None, str(error)
    except Exception as error:
        app.logger.error(f"Failed to execute command '{command}': {error}")
        return None, str(error)

def handle_query_url(request):
    try:
        query = request.args.get('q')
        api_key = request.args.get('api_key')
        temp_path = os.path.join(TEMP_DIR, api_key) + '/'
        final_path = os.path.join(ROOT_DIR, api_key) + '/'
        rip = '/home/linux-server/.local/bin/rip'

        # Ensure temp and final paths exist
        os.makedirs(temp_path, exist_ok=True)
        os.makedirs(final_path, exist_ok=True)

        # Download command using rip
        download_command = f'{rip} --no-progress -f {temp_path} url {query}'
        download_result, d_error = run_command(download_command)

        # Uncomment and adjust these commands as needed
        # Move command
        move_command = f'mv {temp_path}/* {final_path}/'
        move_result, m_error = run_command(move_command, sudo=True)

        # Delete command
        delete_command = f'rm -rf {temp_path}/*'
        delete_result, de_error = run_command(delete_command, sudo=True)

        return jsonify({
            'Downloaded': download_result if download_result else d_error,
            'Move': move_result if move_result else m_error,
            'Delete': delete_result if delete_result else de_error
        })
    except Exception as error:
        return jsonify({
            'Error': str(error),
            'Download': download_command if 'download_command' in locals() else '',
            'Move': move_command if 'move_command' in locals() else '',
            'Delete': delete_command if 'delete_command' in locals() else ''
        })

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

def handle_query_find(request, single= False):
    try:
        query = request.args.get('q')
        single = request.args.get('single', False)
        root = ROOT_DIR + '/' + request.args.get('api_key')
        path = find_file_or_directory(root + query, single)
        return path
    except Exception as error:
        return {'Error': str(error)}   

def handle_query_stream(request):
    try:
        query = request.args.get('q')
        
        path = handle_query_find(request)
        def generate():
            with open(path, "rb") as fogg:
                data = fogg.read(1024)
                while data:
                    yield data
                    data = fogg.read(1024)
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