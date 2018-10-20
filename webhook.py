import json
import os
import requests
import pandas as pd
import numpy as np

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

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
    #return	data.to_json()


def processRequest(req):
    if req.get("result").get("action") == "getcontact":
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
    elif req.get("result").get("action") == "givingAddress":
        result = req.get("result")
        parameters = result.get("parameters")
        idx = list(map(np.all, zip(data["state"]==parameters["state"], data["type"] == parameters["type"]))).index(True)
        address = data.loc[idx, 'address']
        speech = "Here is the address: "+ address
        return  {
                "speech": speech,
                "displayText": speech,
                "source": "webhook"
                }
    elif req.get("result").get("action") == "getPolicy":
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
    else:
        return {}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port, host='0.0.0.0')








"""
import numpy as np
parameters  = {'state':"Tamil Nadu", "type":"R&D Centre"}
data.loc[0,:]




data[(data["state"]==parameters["state"]).index(True)][data["type"] == parameters["type"]]
"""