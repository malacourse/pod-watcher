from pod_bot import PodBot
from flask import Flask
import os
import sys
import traceback
from pod_monitory import PodMonitor

application = Flask(__name__)

@application.route("/")
def status_page():
    retStr =  "<h1>Pod Status Page</h1>"
    retStr +=  "<h2><a href='/config'>Configuration</a></h2>"
    retStr +=  "<h2><a href='/init'>Initialize</a></h2>"

    botStatus = "<p>No Started</p>"
    #try:
    #   botStatus = bot.get_status()
    #except:
    #   print(traceback.format_exc())
    #   status = "Error:" + str(sys.exc_info()[0])
    retStr = retStr + str(botStatus)
    return retStr

@application.route("/config")
def config_page():
    retStr = "OpenShift URL: " + os.environ["OPENSHIFT_URL"] 
    return retStr

@application.route("/init")
def init_page():
    retStr = "Config Status:"
    try:
       botStatus = PodBot().start()
       retStr = retStr + "Success"
    except:
       print(traceback.format_exc())
       retStr = retStr +  "Error:" + str(sys.exc_info()[0])
    return retStr

if __name__ == "__main__":


    application.run()
