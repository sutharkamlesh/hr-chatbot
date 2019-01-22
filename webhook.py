import json
import os
import requests
import pandas as pd
import numpy as np

from flask import Flask
from flask import request
from flask import make_response

data = pd.read_csv("Apollo_locations.csv")
jobs = pd.read_csv("Jobs.csv", encoding = 'latin_1')

policy = {'Leave':'http://hrcouncil.ca/docs/POL_Sick_Leave_YWCA.pdf',
          "Expense":"http://hrcouncil.ca/hr-toolkit/documents/POL_Expenses_0710.doc",
          "Harassment":"http://hrcouncil.ca/docs/POL_Harassment2.pdf"}
office_location = {"Mumbai":"\n Interactive Avenues Pvt. Ltd.,\n 3rd Floor, Chhibber House,\n M Vasanji Road, Opposite Pop Tate’s, \n Near Sakinaka Metro Station,\n Andheri East, Mumbai - 400072.\n Tel: +91 022 - 6264 5000",
                    "Gurgaon": "\n Interactive Avenues Pvt. Ltd.,\n 5th Floor, Plot#15, Sector 44, Institutional Area,\n Gurgaon - 122 012.\n Tel: +91 (124) 4410900",
                    "Bengaluru":"\n Interactive Avenues Pvt. Ltd.,\n 5th Floor, Mateen Tower, Diamond District,\n Old Airport Road, Domlur,\n Bengaluru - 560 008.\n Tel: +91 8042717834 \n Mob: +91 9343797506",
                    "Kolkata":"\n Interactive Avenues Pvt. Ltd.,\n Flat C, Ground Floor, Tivoli Court,\n 1A Ballygunge Circular Road,\n Kolkata- 700019.\n Mob: +91 7044089122"}
office_CP = {
                "Mumbai":{
                    "name":"Harish Iyer",
                    "designation":"Vice President",
                    "email":"harish.iyer@interactiveavenues.com",
                    "phone":"9820466984"
                },
                "Gurgaon": {
                    "name":"Abhishek Chadha",
                    "designation":"Vice President",
                    "email":"abbhishek.chadha@interactiveavenues.com",
                    "phone":"9871117894"
                },
                "Bengaluru":{
                    "name":"Aparna Tadikonda",
                    "designation":"Executive Vice President",
                    "email":"aparna.tadikonda@interactiveavenues.com",
                    "phone":"9343797506"
                },
                "Kolkata":{
                    "name":"Susmita Mukhopadhyay",
                    "designation":"Senior Group Head",
                    "email":"susmita.mukhopadhyay@interactiveavenues.com",
                    "phone":"7044089122"
                }
            }
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

    # Getting Contact details
    if req.get("result").get("action") == "getcontact":
        result = req.get("result")
        parameters = result.get("parameters")
        idx = list(data["state"]==parameters["state"]).index(True)
        contact = data.loc[idx, 'phone']
        speech = "Here it is: "+contact
        return {
                "speech": speech,
                "displayText": speech,
                "source": "webhook",
                }

    # Getting Address
    elif req.get("result").get("action") == "givingAddress":
        result = req.get("result")
        parameters = result.get("parameters")
        idx = list(data["state"]==parameters["state"]).index(True)
        address = data.loc[idx, 'address']
        speech = "Here is the address: "+ address
        return  {
                "speech": speech,
                "displayText": speech,
                "source": "webhook",
                }
    # Get policy details
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
    
    # Getting Address of Office IA
    elif req.get("result").get("action") == "OfficeLocation":
        result = req.get("result")
        parameters = result.get("parameters")
        address = office_location[parameters['location']]
        speech = "Here is the address: "+ address
        return  {
                "speech": speech,
                "displayText": speech,
                "source": "webhook",
                }
    
    # About Company with their website
    elif req.get("result").get("action") == "aboutcompany":
        speech = "A group of people who loved and lived online wanted to change the way you look at it. That’s how IA was formed. Ten years later, that small group has grown to include over 350+ people who share the same passion. And it’s not just passion that we bring to the table. We’ve got some of the most experienced forces on the team and our acquisition by IPG Mediabrands in 2013 has only made us stronger. As the global media holding company of the Interpublic Group, IPG Mediabrands operates in more than 127 countries, giving us the ability to join forces with hundreds of talented marketing professionals within the network"
        return  {
                 "speech": speech,
                 "displayText": speech,
                 "source": "webhook",
                 "data": {"sidebar_url": "http://www.interactiveavenues.com/about-us.html"}
                }
    
    # Giving Contact person details of given office location 
    elif req.get("result").get("action") == "OfficeLocation.OfficeLocation-contact_person":
        result = req.get("result")
        parameters = result.get("parameters")
        speech = "You can talk to "+office_CP[parameters['location']]["name"]+" who is "+office_CP[parameters['location']]["designation"]+" at Interactive Avenues. \n Email: "+office_CP[parameters['location']]["email"]+"\n Phone: "+office_CP[parameters['location']]["phone"]
        return  {
                 "speech": speech,
                 "displayText": speech,
                 "source": "webhook",
                }
    
    # Giving Jobs Details 
    elif req.get("result").get("action") == "jobs":
        result = req.get("result")
        parameters = result.get("parameters")
        location = parameters['location']
        MinExp = parameters['MinExp']["amount"]
        Skills = parameters["Skills"]

        if location:
            job = jobs[jobs['location'] == location][jobs["Skills"] == Skills][jobs["MinExp"] <= MinExp].head(1).to_dict(orient='records')
            speech = "We have job opening for {0} position in {1} with experience ranging between {2} to {3} years.".format(job['JobTitle'], location, job["MinExp"], job["MaxExp"])
        else:
            job = jobs[jobs["Skills"] == Skills][jobs["MinExp"] <= MinExp].to_dict(orient='records')[0]
            speech = "We have job opening for {0} position with experience ranging between {1} to {2} years.".format(job['JobTitle'], job["MinExp"], job["MaxExp"])
        
        return  {
                 "speech": speech,
                 "displayText": speech,
                 "source": "webhook",
                 "data":{"sidebar_url": "http://www.interactiveavenues.com/careers.html"}
                }
    
    elif req.get("result").get("action") == "job_description":
        result = req.get("result")
        parameters = result.get("parameters")
        location = parameters['location']
        MinExp = parameters['MinExp']["amount"]
        Skills = parameters["Skills"]

        if location:
            job = jobs[jobs['location'] == location][jobs["Skills"] == Skills][jobs["MinExp"] >= MinExp].head(1).to_dict(orient='records')
            speech = "Job Description: " + job['JobDescription']
        else:
            job = jobs[jobs["Skills"] == Skills][jobs["MinExp"] >= MinExp].to_dict(orient='records')[0]
            speech = "Job Description: " + job['JobDescription']
        
        return  {
                 "speech": speech,
                 "displayText": speech,
                 "source": "webhook",
                 "data":{"sidebar_url": "http://www.interactiveavenues.com/careers.html"}
                }
    
    elif req.get("result").get("action") == "JobsEnquiry.Salary":
        result = req.get("result")
        parameters = result.get("parameters")
        location = parameters['location']
        MinExp = parameters['MinExp']["amount"]
        Skills = parameters["Skills"]

        if location:
            job = jobs[jobs['location'] == location][jobs["Skills"] == Skills][jobs["MinExp"] >= MinExp].head(1).to_dict(orient='records')
            speech = "Salary range: " + job['MinSalary'] + " to " + job['MaxSalary']
        else:
            job = jobs[jobs["Skills"] == Skills][jobs["MinExp"] >= MinExp].to_dict(orient='records')[0]
            speech = "Job Description: " + job['JobDescription']
        
        return  {
                 "speech": speech,
                 "displayText": speech,
                 "source": "webhook",
                 "data":{"sidebar_url": "http://www.interactiveavenues.com/careers.html"}
                }

    else:
        return {}


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port, host='0.0.0.0')

#parameters={"Skills": "Design","MinExp": {"amount": 2,"unit": "yr"},"location": ""}
