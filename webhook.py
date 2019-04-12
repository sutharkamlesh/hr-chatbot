import json
import os
import requests
import pandas as pd
import numpy as np

from flask import Flask
from flask import request
from flask import make_response

data = pd.read_csv("Apollo_locations.csv")
jobs = pd.read_csv("Jobs.csv", encoding='latin_1')

policy = {'Leave': 'http://hrcouncil.ca/docs/POL_Sick_Leave_YWCA.pdf',
          "Expense": "http://hrcouncil.ca/hr-toolkit/documents/POL_Expenses_0710.doc",
          "Harassment": "http://hrcouncil.ca/docs/POL_Harassment2.pdf"}

office_location = {
                    "Mumbai": "\n Interactive Avenues Pvt. Ltd.,\n 3rd Floor, Chhibber House,\n M Vasanji Road, Opposite Pop Tate’s, \n Near Sakinaka Metro Station,\n Andheri East, Mumbai - 400072.\n Tel: +91 022 - 6264 5000",
                    "Gurgaon": "\n Interactive Avenues Pvt. Ltd.,\n 5th Floor, Plot#15, Sector 44, Institutional Area,\n Gurgaon - 122 012.\n Tel: +91 (124) 4410900",
                    "Bengaluru": "\n Interactive Avenues Pvt. Ltd.,\n 5th Floor, Mateen Tower, Diamond District,\n Old Airport Road, Domlur,\n Bengaluru - 560 008.\n Tel: +91 8042717834 \n Mob: +91 9343797506",
                    "Kolkata": "\n Interactive Avenues Pvt. Ltd.,\n Flat C, Ground Floor, Tivoli Court,\n 1A Ballygunge Circular Road,\n Kolkata- 700019.\n Mob: +91 7044089122"
                }

office_CP = {
                "Mumbai": {
                    "name": "Harish Iyer",
                    "designation": "Vice President",
                    "email": "harish.iyer@interactiveavenues.com",
                    "phone": "9820466984"
                },
                "Gurgaon": {
                    "name": "Abhishek Chadha",
                    "designation": "Vice President",
                    "email": "abbhishek.chadha@interactiveavenues.com",
                    "phone": "9871117894"
                },
                "Bengaluru": {
                    "name": "Aparna Tadikonda",
                    "designation": "Executive Vice President",
                    "email": "aparna.tadikonda@interactiveavenues.com",
                    "phone": "9343797506"
                },
                "Kolkata": {
                    "name": "Susmita Mukhopadhyay",
                    "designation": "Senior Group Head",
                    "email": "susmita.mukhopadhyay@interactiveavenues.com",
                    "phone": "7044089122"
                }
            }

# Getting years of experience
def exp2years(exp_dict):
    if exp_dict['unit'] == 'yr':
        return exp_dict['amount']
    elif exp_dict['unit'] == "mo":
        return exp_dict['amount']/12
    elif exp_dict['unit'] == 'days':
        return exp_dict['amount']/365
    else:
        return None


# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    # print(json.dumps(req, indent=4))
    res = process_request(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r
    # return data.to_json()


def process_request(req):
    try:
        # Getting Contact details
        if req.get("result").get("action") == "getcontact":
            result = req.get("result")
            parameters = result.get("parameters")
            idx = list(data["state"] == parameters["state"]).index(True)
            contact = data.loc[idx, 'phone']
            speech = "Here it is: "+contact
            return {
                    "speech": speech,
                    "displayText": speech,
                    "source": "webhook",
                    }

        # Getting Address
        # elif req.get("result").get("action") == "givingAddress":
        #     result = req.get("result")
        #     parameters = result.get("parameters")
        #     idx = list(data["state"] == parameters["state"]).index(True)
        #     address = data.loc[idx, 'address']
        #     speech = "Here is the address: " + address
        #     return {
        #         "speech": speech,
        #         "displayText": speech,
        #         "source": "webhook"
        #     }
        # Get policy details
        # elif req.get("result").get("action") == "getPolicy":
        #     result = req.get("result")
        #     parameters = result.get("parameters")
        #     if parameters['policy'] in policy.keys():
        #         speech = "You can see our " + parameters['policy'] + " policy from here: " + policy[parameters['policy']]
        #     else:
        #         speech = "Sorry we don't have this information"
        #     return {
        #             "speech": speech,
        #             "displayText": speech,
        #             "source": "webhook",
        #             "data": {"sidebar_url": policy[parameters['policy']]}
        #             }

        # Getting Address of Office IA
        elif req.get("result").get("action") == "OfficeLocation":
            result = req.get("result")
            parameters = result.get("parameters")
            if parameters['location']:
                address = office_location[parameters['location']]
                speech = "Here is the address: " + address
                return {
                    "speech": speech,
                    "displayText": speech,
                    "source": "webhook",
                    'messages': [
                        {
                            "type": 0,
                            "platform": "slack",
                            "speech": "Please Choose the Location you want to visit:"
                        },
                        {
                            "type": 1,
                            "platform": "slack",
                            "buttons": [
                                {
                                    "text": "Talk to Contact Person their?",
                                    "postback": "Give me contact details from this office."
                                },
                                {
                                    "text": "What else can you do?",
                                    "postback": "What else can you do?"
                                }
                            ]
                        }
                    ]
                }
            else:
                return {
                    "speech": "Please Choose the Location you want to visit:",
                    "displayText": "Choose Location:",
                    "source": "webhook",
                    'messages': [
                        {
                            "type": 0,
                            "platform": "slack",
                            "speech": "Please Choose the Location you want to visit:"
                        },
                        {
                            "type": 1,
                            "platform": "slack",
                            "buttons": [
                                {
                                    "text": "Mumbai",
                                    "postback": "Where is your office located in Mumbai?"
                                },
                                {
                                    "text": "Gurgaon",
                                    "postback": "Where is your office located in Gurgaon?"
                                },
                                {
                                    "text": "Kolkata",
                                    "postback": "Where is your office located in Kolkata?"
                                },
                                {
                                    "text": "Bengaluru",
                                    "postback": "Where is your office located in Bengaluru"
                                }
                            ]
                        }
                    ]
                }

        # About Company with their website
        # elif req.get("result").get("action") == "aboutcompany":
        #     speech = """A group of people who loved and lived online wanted to change the way you look at it.
        #                 That’s how IA was formed. Ten years later, that small group has grown to include over
        #                 350+ people who share the same passion. And it’s not just passion that we bring to the
        #                 table. We’ve got some of the most experienced forces on the team and our acquisition by
        #                 IPG Mediabrands in 2013 has only made us stronger. As the global media holding company
        #                 of the Interpublic Group, IPG Mediabrands operates in more than 127 countries, giving us
        #                 the ability to join forces with hundreds of talented marketing professionals within the
        #                 network."""
        #     return {
        #                 "speech": speech,
        #                 "displayText": speech,
        #                 "source": "webhook",
        #                 "data": {"sidebar_url": "http://www.interactiveavenues.com/about-us.html"},
        #                 'messages': [
        #                     {
        #                         "type": 1,
        #                         "platform": "slack",
        #                         "buttons": [
        #                             {
        #                                 "text": "Know benefits of working in IA",
        #                                 "postback": "what are the benefits of working in IA?"
        #                             },
        #                             {
        #                                 "text": "What else can you do?",
        #                                 "postback": "What else can you do?"
        #                             }
        #                         ]
        #                     }
        #                 ]
        #             }

        # Giving Contact person details of given office location
        elif req.get("result").get("action") == "OfficeLocation.OfficeLocation-contact_person":
            result = req.get("result")
            parameters = result.get("parameters")
            speech = "You can talk to " + [parameters['location']]["name"] + " who is " + office_CP[parameters['location']]["designation"] + " at Interactive Avenues. \n Email: " + office_CP[parameters['location']]["email"] + "\n Phone: " + office_CP[parameters['location']]["phone"]
            return {
                        "speech": speech,
                        "displayText": speech,
                        "source": "webhook",
                        'messages': [
                            {
                                "type": 1,
                                "platform": "slack",
                                "buttons": [
                                    {
                                        "text": "What else can you do?",
                                        "postback": "What else can you do?"
                                    }
                                ]
                            },
                            {
                                "type": 2,
                                "platform": "facebook",
                                # "title": "",
                                "replies": [
                                    "I need more help"
                                ]
                            }
                        ]
                    }
        elif req.get("result").get("action") == "OfficeLocation.OfficeLocation-google_direction":
            speech = "Opening Google Maps..."
            return {
                        "speech": speech,
                        "displayText": speech,
                        "source": "webhook",
                        "data":{
                            "sidebar_url": "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d6344.533126193033!2d72.81876138673469!3d18.99847234035681!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3be7ce857702f139%3A0x6757363917fb70ca!2sTechmatters+Technologies!5e0!3m2!1sen!2sin!4v1550735226214"
                        },
                        'messages': [
                            {
                                "type": 1,
                                "platform": "slack",
                                "buttons": [
                                    {
                                        "text": "What else can you do?",
                                        "postback": "What else can you do?"
                                    }
                                ]
                            },
                            {
                                "type": 2,
                                "platform": "facebook",
                                "title": "Google Maps: https://www.google.com/maps/place/Techmatters+Technologies/@18.9977195,72.8183079,15.5z/data=!4m12!1m6!3m5!1s0x0:0x6757363917fb70ca!2sTechmatters+Technologies!8m2!3d18.9962875!4d72.8152659!3m4!1s0x0:0x6757363917fb70ca!8m2!3d18.9962875!4d72.8152659",
                                "replies": [
                                    "I need more help"
                                ]
                            }
                        ]
                    }

        elif req.get("result").get("action") == "visit.home.page":
            speech = "You see Qrata Page on rightside window. "
            return {
                        "speech": speech,
                        "displayText": speech,
                        "source": "webhook",
                        "data":{
                            "sidebar_url": "http://qrata.co/in/"
                        },
                        'messages': [
                            {
                                "type": 1,
                                "platform": "slack",
                                "buttons": [
                                    {
                                        "text": "What else can you do?",
                                        "postback": "What else can you do?"
                                    }
                                ]
                            },
                            {
                                "type": 2,
                                "platform": "facebook",
                                # "title": "",
                                "replies": [
                                    "What else can you do?"
                                ]
                            }
                        ]
                    }

        # Giving Jobs Details
        elif req.get("result").get("action") == "jobs":
            result = req.get("result")
            parameters = result.get("parameters")
            location = parameters['location']
            min_exp = exp2years(parameters['MinExp'])
            skills = parameters["Skills"]

            if location:
                try:
                    job = jobs[jobs['Location'] == location][jobs["Skills"] == skills][jobs["MinExp"] <= min_exp].head(1).to_dict(orient='records')[0]
                    speech = """We have job opening for {0} position in {1} with experience ranging 
                                between {2} to {3} years.""".format(job['JobTitle'], location, job["MinExp"], job["MaxExp"])
                except:
                    return {
                        "speech": "Sorry, we don't have job opening for you in {0} at {1}".format(skills, location),
                        "displayText": "Sorry, we don't have job opening for you in {0} at {1}".format(skills, location),
                        "source": "webhook",
                        'messages': [
                            {
                                "type": 1,
                                "platform": "slack",
                                "buttons": [
                                    {
                                        "text": "Look for another job",
                                        "postback": "I am looking for jobs in Qrata"
                                    }
                                ]
                            },
                            {
                                "type": 2,
                                "platform": "facebook",
                                # "title": "",
                                "replies": [
                                    "Look for another job"
                                ]
                            }
                        ]
                    }
            else:
                return {
                    "speech": "Choose your preferred  location for the job:",
                    "displayText": "Choose your preferred location for the job:",
                    "source": "webhook",
                    #"data": {"sidebar_url": "http://www.interactiveavenues.com/careers.html"},
                    'messages': [
                        {
                            "type": 0,
                            "platform": "slack",
                            "speech": "Choose your preferred location for the job:"
                        },
                        {
                            "type": 1,
                            "platform": "slack",
                            "buttons": [
                                {
                                    "text": "Mumbai",
                                    "postback": "Looking for a job in {0} for around {1} years of experience in Mumbai".format(skills, min_exp)
                                },
                                {
                                    "text": "Kolkata",
                                    "postback": "Looking for a job in {0} for around {1} years of experience in Kolkata".format(skills, min_exp)
                                },
                                {
                                    "text": "Gurgaon",
                                    "postback": "Looking for a job in {0} for around {1} years of experience in Gurgaon".format(skills, min_exp)
                                },
                                {
                                    "text": "Bengaluru",
                                    "postback": "Looking for a job in {0} for around {1} years of experience in Bengaluru".format(skills, min_exp)
                                }
                            ]
                        }
                    ]
                }

            return {
                        "speech": speech,
                        "displayText": speech,
                        "source": "webhook",
                        # "data": {"showButton": True, "sidebar_url": "http://www.interactiveavenues.com/careers.html"},
                        'messages': [
                            {
                                "type": 1,
                                "platform": "slack",
                                "buttons": [
                                    {
                                        "text": "Job Decription",
                                        "postback": "I want to see Job Description"
                                    },
                                    {
                                        "text": "Salary Range",
                                        "postback": "The salary for this Job"
                                    }
                                ]
                            },
                            {
                                "type": 2,
                                "platform": "facebook",
                                "replies": [
                                    "See Job Description",
                                    "Salary for this Job"
                                ]
                            }
                        ]
                    }

        elif req.get("result").get("action") == "job_description":
            result = req.get("result")
            contexts = result.get("contexts")[0]
            parameters = contexts["parameters"]
            location = parameters['location']
            min_exp = exp2years(parameters['MinExp'])
            skills = parameters["Skills"]

            if location:
                job = jobs[jobs['Location'] == location][jobs["Skills"] == skills][jobs["MinExp"] <= min_exp].head(1).to_dict(orient='records')[0]
                speech = "Job Description: " + job['JobDescription']
            else:
                job = jobs[jobs["Skills"] == skills][jobs["MinExp"] <= min_exp].head(1).to_dict(orient='records')[0]
                speech = "Job Description: " + job['JobDescription']

            return {
                        "speech": speech,
                        "displayText": speech,
                        "source": "webhook",
                        # "data": {"sidebar_url": "http://www.interactiveavenues.com/careers.html"},
                        'messages': [
                            {
                                "type": 1,
                                "platform": "slack",
                                "buttons": [
                                    {
                                        "text": "What else can I do for you?",
                                        "postback": "What else can I do for you?"
                                    },
                                    {
                                        "text": "Salary Range",
                                        "postback": "The salary for this Job"
                                    }
                                ]
                            },
                            {
                                "type": 2,
                                "platform": "facebook",
                                "replies": [
                                    "Salary for this Job",
                                    "What else you can do?"
                                ]
                            }
                        ]
                    }
        elif req.get("result").get("action") == "AllJobs":
            speech = "We have various types of jobs available and we are always ready to hire smart candidates. You can browse through various jobs and apply for the job you liked most."
            return {
                "speech": speech,
                "displayText": speech,
                "source": "webhook",
                # "data": {"showButton": True, "sidebar_url":"http://www.interactiveavenues.com/careers.html"},
                'messages': [
                    {
                        "type": 1,
                        "platform": "slack",
                        "buttons": [
                                        {
                                            "text": "Search a job",
                                            "postback": "Search a job for me"
                                        },
                                        {
                                            "text": "What else you can do?",
                                            "postback": "What else you can do?"
                                        }
                                    ]
                    },
                    {
                        "type": 2,
                        "platform": "facebook",
                        "title": "Visit link to see Qrata jobs",
                        "buttons": [
                            {
                                "text": "Visit link",
                                "postback": "https://www.google.com/search?q=qrata+jobs&rlz=1C1CHZL_enIN740IN740&oq=qrata+jobs&aqs=chrome.0.69i59j69i60j0.9069j0j7&sourceid=chrome&ie=UTF-8&ibp=htl;jobs&sa=X&ved=2ahUKEwiyzdub_cTgAhUaTn0KHV3KBBMQiYsCKAB6BAgBEAM#fpstate=tldetail&htidocid=lfUi4RU4zzif1-e7AAAAAA%3D%3D&htivrt=jobs"
                            }
                        ]
                    }
                ]
            }
        elif req.get("result").get("action") == "JobsEnquiry.Salary":
            result = req.get("result")
            contexts = result.get("contexts")[0]
            parameters = contexts["parameters"]
            location = parameters['location']
            min_exp = exp2years(parameters['MinExp'])
            skills = parameters["Skills"]

            if location:
                job = jobs[jobs['Location'] == location][jobs["Skills"] == skills][jobs["MinExp"] <= min_exp].head(1).to_dict(orient='records')[0]
                speech = "Salary range: Rs." + str(job['MinSalary']) + " to Rs." + str(job['MaxSalary'])
            else:
                job = jobs[jobs["Skills"] == skills][jobs["MinExp"] <= min_exp].head(1).to_dict(orient='records')[0]
                speech = "Salary range: Rs." + str(job['MinSalary']) + " to Rs." + str(job['MaxSalary'])

            return {
                        "speech": speech,
                        "displayText": speech,
                        "source": "webhook",
                        # "data": {"sidebar_url": "http://www.interactiveavenues.com/careers.html"},
                        'messages': [
                            {
                                "type": 1,
                                "platform": "slack",
                                "buttons": [
                                    {
                                        "text": "What else can I do for you?",
                                        "postback": "What else can I do for you?"
                                    },
                                    {
                                        "text": "Job Decription",
                                        "postback": "I want to see Job Description"
                                    }
                                ]
                            }
                        ]
                    }

        else:
            return {}
    except Exception as e:
        print("Error:", e)
        return {
            "speech": "Oops...I am not able to help you at the moment, please try again..",
            "displayText": "Oops...I am not able to help you at the moment, please try again..",
            "source": "webhook",
        }



if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port {}".format(port))
    app.run(debug=False, port=port, host='0.0.0.0')

# parameters={"Skills": "Marketing","MinExp": {"amount": 4,"unit": "yr"},"location": ""}
