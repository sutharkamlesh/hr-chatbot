import json
import os
import requests
import pandas as pd

from flask import Flask
from flask import request
from flask import make_response

data = pd.read_csv("Apollo_locations.csv")

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    #print(json.dumps(req, indent=4))

    if req.get("result").get("action") != "getcontact":
        res = get_contact(req)
    elif req.get("result").get("action") != "givingAddress":
        res = get_address(req)
    
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
    #return	data.to_json()

def get_address(req):
    if req.get("result").get("action") != "givingAddress":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    address = data[data["state"]==parameters["state"]][data["type"] == parameters["type"]].to_string()
    if address.split()[0] != 'Empty':
        speech = "Here is the address: "+data[data["state"]==parameters["state"]][data["type"] == parameters["type"]]['address'].to_string()
    else:
        speech = "Sorry we don't have this information"
    return  {
    "speech": speech,
    "displayText": speech,
    "source": "apiai-weather-webhook"
    }

def get_contact(req):
    if req.get("result").get("action") != "getcontact":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    address = data[data["state"]==parameters["state"]][data["type"] == parameters["type"]].to_string()
    if address.split()[0] != 'Empty':
        speech = "Here it is: "+data[data["state"]==parameters["state"]][data["type"] == parameters["type"]]['phone'].to_string()
    else:
        speech = "Sorry we don't have this information"
    return {
    "speech": speech,
    "displayText": speech,
    "source": "apiai-weather-webhook"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port, host='0.0.0.0')

















