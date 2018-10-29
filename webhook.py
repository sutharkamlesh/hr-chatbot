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
office_location = {"Mumbai":"Interactive Avenues Pvt. Ltd.,\n 3rd Floor, Chhibber House,\n M Vasanji Road, Opposite Pop Tate’s, \n Near Sakinaka Metro Station,\n Andheri East, Mumbai - 400072.\n Tel: +91 022 - 6264 5000",
                    "Gurgaon": "Interactive Avenues Pvt. Ltd.,\n 5th Floor, Plot#15, Sector 44, Institutional Area,\n Gurgaon - 122 012.\n Tel: +91 (124) 4410900",
                    "Bengaluru":"Interactive Avenues Pvt. Ltd.,\n 5th Floor, Mateen Tower, Diamond District,\n Old Airport Road, Domlur,\n Bengaluru - 560 008.\n Tel: +91 8042717834 \n Mob: +91 9343797506",
                    "Kolkata":"Interactive Avenues Pvt. Ltd.,\n Flat C, Ground Floor, Tivoli Court,\n 1A Ballygunge Circular Road,\n Kolkata- 700019.\n Mob: +91 7044089122"}

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
        idx = list(data["state"]==parameters["state"]).index(True)
        contact = data.loc[idx, 'phone']
        speech = "Here it is: "+contact
        return {
                "speech": speech,
                "displayText": speech,
                "source": "webhook"
                }
    elif req.get("result").get("action") == "givingAddress":
        result = req.get("result")
        parameters = result.get("parameters")
        idx = list(data["state"]==parameters["state"]).index(True)
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
                "source": "webhook",
                "data": {"sidebar_url": policy[parameters['policy']]}
                }
    elif req.get("result").get("action") == "OfficeLocation":
        result = req.get("result")
        parameters = result.get("parameters")
        address = office_location[parameters['location']]
        speech = "Here is the address: "+ address
        return  {
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