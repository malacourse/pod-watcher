from pod_bot import PodBot
from flask import Flask
from pod_status_reader import PodStatusReader
import os
import sys
import traceback

bot = PodBot().start()
application = Flask(__name__)

@application.route("/")
def status_page():
    retStr =  "<h1>Pod Status Page</h1>"
    retStr +=  "<h2><a href='/config'>Configuration</a></h2>"
    
    threshold = 1
    if "RESTART_THRESHOLD" in os.environ:
           threshold = os.environ["RESTART_THRESHOLD"]

    status = "<p>No Status</p>"
    try:
       items = PodStatusReader().get_status()
       if type(items) == dict:
           status = "<table><tr><td>Name</td><td>Restart Count</td><td>State</td></tr>"
           for key, ps in items.iteritems():
               #status += "<tr>"
               status += "<tr>" if ps["restartCount"] < threshold else "<tr style='color:#ff0000;'>"
               status += "<td>" +str(key) + "</td><td>" + str(ps["restartCount"]) + "</td><td>" + str(ps["state"]) + "</td>" 
               status += "</tr>"
           status += "</table>"

    except:
       print(traceback.format_exc())
       status = "Error:" + str(sys.exc_info()[0])
    retStr = retStr + str(status)
    return retStr

@application.route("/config")
def config_page():
    retStr = "OpenShift URL: " + os.environ["OPENSHIFT_URL"] 
    return retStr

if __name__ == "__main__":
    application.run()
