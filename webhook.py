import json
import os
import requests
import pandas as pd

from flask import Flask
from flask import request
from flask import make_response

data = pd.read_csv("Apollo_locations.csv")
policy = {'Leave':'http://hrcouncil.ca/docs/POL_Sick_Leave_YWCA.pdf',
          "Expense":"http://hrcouncil.ca/hr-toolkit/documents/POL_Expenses_0710.doc",
          "Harassment":"http://hrcouncil.ca/docs/POL_Harassment2.pdf"}
# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    #print(json.dumps(req, indent=4))

    if req.get("result").get("action") == "getcontact":
        res = get_contact(req)
    elif req.get("result").get("action") == "givingAddress":
        res = get_address(req)
    elif req.get("result").get("action") == "getPolicy":
        res = get_policy(req)
    else:
        res = {}

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
    #return	data.to_json()

def get_address(req):
    result = req.get("result")
    parameters = result.get("parameters")
    address = data[data["state"]==parameters["state"]][data["type"] == parameters["type"]].to_string()
    if address.split()[0] != 'Empty':
        speech = "Here is the address: "+data[data["state"]==parameters["state"]][data["type"] == parameters["type"]]['address'].to_string()[1:]
    else:
        speech = "Sorry we don't have this information"
    return  {
    "speech": speech,
    "displayText": speech,
    "source": "webhook"
    }

def get_contact(req):
    result = req.get("result")
    parameters = result.get("parameters")
    address = data[data["state"]==parameters["state"]][data["type"] == parameters["type"]].to_string()
    if address.split()[0] != 'Empty':
        speech = "Here it is: "+data[data["state"]==parameters["state"]][data["type"] == parameters["type"]]['phone'].to_string()[1:]
    else:
        speech = "Sorry we don't have this information"
    return {
    "speech": speech,
    "displayText": speech,
    "source": "webhook"
    }

def get_policy(req):
    result = req.get("result")
    parameters = result.get("parameters")
    if parameters['policy'] in policy.keys():
        speech = "You can see our "+ parameters['policy'] +" policy from here: " + policy[parameters['policy']]
    else:
        speech = "Sorry we don't have this information"
    return {
    "speech": speech,
    "displayText": speech,
    "source": "webhook"
    }
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port, host='0.0.0.0')

















