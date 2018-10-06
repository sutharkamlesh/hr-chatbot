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

    res = get_address(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
    #return	data.to_json()

def get_address(req):
    #if req.get("result").get("action") != "fetchWeatherForecast":
    #    return {}
    result = req.get("result")
    parameters = result.get("parameters")
    address = data[data["state"]==parameters["state"]][data["type"] == parameters["type"]]["address"].to_string()
    speech = "Here is the address: "+address
    return {'fulfillmentText': speech}

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port)

















