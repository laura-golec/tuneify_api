from flask import Flask, request, jsonify, stream_with_context, render_template, url_for
import os
import time
import sys 
import errno 
import asyncio
from waitress import serve
from logging.config import dictConfig

from api_handlers import *
from helper_functions import validate_api_key


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s | %(module)s >>> %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",

            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file": {

                "class": "logging.FileHandler",

                "filename": "flask.log",

                "formatter": "default",

            },

        },
        "root": {"level": "DEBUG", "handlers": ["console", "file"]},

    }
)

app = Flask(__name__)
app.json.sort_keys = False
app.config['SERVER_NAME'] = 'tuneify.lauragolec.com'

@app.route(f'/', methods=['GET'])
async def tuneify_home():
    return render_template('index.html')

@app.route(f'/search/', methods=['GET'])
def search():
    if validate_api_key(request.args.get('api_key')):
        response, _ = handle_query_search(request)
        return response.data
    return jsonify({'Error': 'Access Denied'}), 403

@app.route(f'/ipod/', methods=['GET'])
def ipod():
    return handle_query_ipod(request)

@app.route(f'/download/', methods=['GET'])
def download():
    if validate_api_key(request.args.get('api_key')):
        response = handle_query_download(request)
        return response
    return jsonify({'Error': 'Access Denied'}), 403

@app.route(f'/url/', methods=['GET'])
def url():
    if validate_api_key(request.args.get('api_key')):
        app.logger.debug("A debug message")
        return handle_query_url(request)
    return jsonify({'Error': 'Access Denied'}), 403

@app.route(f'/browse/', methods=['GET'])
def browse():
    if validate_api_key(request.args.get('api_key')):
        response = handle_query_browse(request)
        return response
    return jsonify({'Error': 'Access Denied'}), 403

@app.route(f'/config/', methods=['GET'])
def config():
    if validate_api_key(request.args.get('api_key')):
        response = handle_query_config(request)
        return response
    return jsonify({'Error': 'Access Denied'}), 403

@app.route(f'/confirm/', methods=['GET'])
def confirm():
    return jsonify({'Connection to Server': 'Established'})

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=5000)
