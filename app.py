from flask import Flask, request, jsonify, stream_with_context, render_template, url_for
import os
import schedule
import time
import sys 
import errno 
import asyncio

from api_handlers import *
from helper_functions import validate_api_key

app = Flask(__name__)
app.json.sort_keys = False
app.config['SERVER_NAME'] = 'api.lauragolec.com'

api_name = 'tuneify_api'

# Schedule the cleanup task to run every day at 3:00 AM
schedule.every().day.at("03:00").do(cleanup_files)

async def scheduled_clean_up():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

@app.route(f'/{api_name}/', methods=['GET'])
async def tuneify_home():
    scheduled_clean_up()
    return render_template('index.html')

@app.route(f'/{api_name}/search/', methods=['GET'])
def search():
    if validate_api_key(request.args.get('api_key')):
        response, _ = handle_query_search(request)
        return response.data
    return jsonify({'Error': 'Access Denied'}), 403

@app.route(f'/{api_name}/ipod/', methods=['GET'])
def ipod():
    return handle_query_ipod(request)

@app.route(f'/{api_name}/download/', methods=['GET'])
def download():
    return handle_query_download(request)

@app.route(f'/{api_name}/url/', methods=['GET'])
def url():
    return handle_query_url(request)

@app.route(f'/{api_name}/browse/', methods=['GET'])
def browse():
    if validate_api_key(request.args.get('api_key')):
        response = handle_query_browse(request)
        return response
    return jsonify({'Error': 'Access Denied'}), 403

@app.route(f'/{api_name}/config/', methods=['GET'])
def config():
    return handle_query_config(request)

@app.route(f'/{api_name}/confirm/', methods=['GET'])
def confirm():
    return jsonify({'Connection to Server': 'Established'})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except IOError as e: 
        if e.errno == errno.EPIPE: 
            pass
