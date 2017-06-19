from pod_bot import PodBot
from flask import Flask
import os
import sys
import traceback

application = Flask(__name__)

@application.route("/")
def status_page():
    retStr =  "<h1>Pod Status Page</h1>"
    retStr +=  "<h2><a href='/config'>Configuration</a></h2>"
    bot = PodBot()
    botStatus = "<p>No Status</p>"
    try:
       botStatus = bot.get_status()
    except:
       print(traceback.format_exc())
       status = "Error:" + str(sys.exc_info()[0])
    retStr = retStr + str(botStatus)
    return retStr

@application.route("/config")
def config_page():
    retStr = "OpenShift URL: " + os.environ["OPENSHIFT_URL"] 
    return retStr

if __name__ == "__main__":
    application.run()
