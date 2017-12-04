# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response
import sys

import logging
from logging.handlers import RotatingFileHandler

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['GET'])
def getwebhook1():
    return 'Hello Webhook'

@app.route('/', methods=['GET'])
def getwebhook2():
    return 'Hello Webhook Default url .. changed on 4th dec 2017 at 4.05 pm'

@app.route('/test', methods=['GET'])
def getwebhook3():
    app.logger.info('in test')
    return 'Hello Webhook Test'

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    app.logger.info("in webhook")

    print("Request:")
    print(json.dumps(req, indent=4))

    if req.get("result").get("action") == 'salary_check':
        res = processSalary(req)
    else:
        res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    sys.stdout.flush()
    return r

def processSalary(req):
    result = req.get("result")
    parameters = result.get("parameters")
    salary = parameters.get("salary")
    if salary >= 25000 :
        speech ='You are eligible for Loan'
    else:
        speech ='We are sorry, You are not eligible for Loan'
    
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }
    sys.stdout.flush()

def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    sys.stdout.flush()
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None
    sys.stdout.flush()
    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(speech)
    sys.stdout.flush()
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    logHandler = RotatingFileHandler('/app/info.log', maxBytes=1000, backupCount=1)
    
    # set the log handler level
    logHandler.setLevel(logging.INFO)
    print('hello... welcome to this app... have a nice day!!')
    # set the app logger level
    app.logger.setLevel(logging.INFO)

    app.logger.addHandler(logHandler)  

    app.logger.info('Hiii.. app started')
    sys.stdout.flush()
    app.run(debug=True, port=port, host='0.0.0.0')
    
