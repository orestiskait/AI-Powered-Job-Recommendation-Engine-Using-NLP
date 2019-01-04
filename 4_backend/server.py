#!/usr/bin/env python
from flask import Flask
from flask import make_response
from flask import request
import json
import base64
import lambda_function

app = Flask(__name__)

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = '*'
    header['Content-Type'] = 'application/json'
    return response

@app.route("/stats", methods=['GET'])
def stats():
    # Create mock event to simulate API Gateway request
    event = {
        "params": {
            "querystring": {
                "skill": request.args.get('skill')
            }
        },
        "context":{
            "resource-path": "/stats"
        }
    }

    resp = make_response(json.dumps(lambda_function.lambda_handler(event, {})))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route("/submit-resume", methods=['POST'])
def submitResume():
    binary = request.get_data()

    base64body = base64.b64encode(binary).decode('ascii')

    # Create mock event to simulate API Gateway request
    event = {
        "body": base64body,
        "params": {
            "header": {
                "content-type": request.headers.get('Content-Type')
            }
        },
        "context":{
            "resource-path": "/submit-resume"
        }
    }

    return json.dumps(lambda_function.lambda_handler(event, {}))
