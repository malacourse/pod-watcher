from pod_monitor import PodMonitor
from flask import Flask, Response
from pod_status_reader import PodStatusReader
import os
import sys
import traceback
import json

monitor = PodMonitor().start()
application = Flask(__name__)

@application.route("/test")
def default_page():
    retStr =  "<h1>Pod Status Page</h1>"
    retStr +=  "<h2><a href='/config'>Configuration</a></h2>"
    
    threshold = 1
    if "RESTART_THRESHOLD" in os.environ:
           threshold = int(os.environ["RESTART_THRESHOLD"])

    status = "<p>No Status</p>"
    try:
       items = PodStatusReader().get_status()
       if type(items) == list:
           status = "<table><tr><td>Name</td><td>Restart Count</td><td>State</td></tr>"
           for ps in items:
               #status += "<tr>"
               status += "<tr>" if ps["restartCount"] < threshold else "<tr style='color:#ff0000;'>"
               status += "<td>" + ps["podName"] + "</td><td>" + str(ps["restartCount"]) + "</td><td>" + str(ps["state"]) + "</td>" 
               status += "</tr>"
           status += "</table>"

    except:
       print(traceback.format_exc())
       status = "Error:" + str(sys.exc_info()[0])
    retStr = retStr + str(status)
    return retStr

def get_current_config():
    threshold = 5
    configMinutes = 720
    config = {}
    if "OPENSHIFT_HOST" in os.environ:
        osHost = os.environ["OPENSHIFT_HOST"]
        config["host"] = osHost
    if "OPENSHIFT_NAMESPACE" in os.environ:
        osNs = os.environ["OPENSHIFT_NAMESPACE"]
        config["namespace"] = osNs
    if "RESTART_THRESHOLD" in os.environ:
        threshold = int(os.environ["RESTART_THRESHOLD"])
    if "RESTART_TIMEFRAME" in os.environ:
        configMinutes = int(os.environ["RESTART_TIMEFRAME"])
    config["timeframe"] = configMinutes
    config["threshold"] = threshold
    return config

    
@application.route("/status")
def status_service():
    threshold = 1
    if "RESTART_THRESHOLD" in os.environ:
           threshold = int(os.environ["RESTART_THRESHOLD"])

    config = get_current_config()
    status = '{"status" : "None"}'
    try:
       items = PodStatusReader().get_status()
       if type(items) == list:
           status = '{"pods" : ' + json.dumps(items) + ',"config" :'  + json.dumps(config) + '}'
       return status
    except:
       print(traceback.format_exc())
       status = "Error:" + str(traceback.format_exc())
    return status
    
@application.route("/pod-restart-alerts")
def restart_alerts():
    threshold = 1
    if "RESTART_THRESHOLD" in os.environ:
           threshold = int(os.environ["RESTART_THRESHOLD"])

    status = '{"status" : "None"}'
    try:
       status = PodStatusReader().get_alerts()
    except:
       print(traceback.format_exc())
       status = '{"status" : "Pod Monitor Error"}'
    return status


@application.route("/config")
def config_page():
    retStr = "<table><tr><td>Name</td><td></tr>"
    if "OPENSHIFT_HOST" in os.environ:
        retStr += "<tr><td>OPENSHIFT_HOST</td><td>" + os.environ["OPENSHIFT_HOST"] + "</td></tr>"
    if "OPENSHIFT_NAMESPACE" in os.environ:
        retStr += "<tr><td>OPENSHIFT_NAMESPACE</td><td>" + os.environ["OPENSHIFT_NAMESPACE"] + "</td></tr>"
    if "OPENSHIFT_TOKEN" in os.environ:
        retStr += "<tr><td>OPENSHIFT_TOKEN</td><td>" + os.environ["OPENSHIFT_TOKEN"] + "</td></tr>"
    if "RESTART_THRESHOLD" in os.environ:
        retStr += "<tr><td>THRESHOLD</td><td>" + os.environ["RESTART_THRESHOLD"] + "</td></tr>"
    retStr += "</table>"
    return retStr

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

def get_file(filename):  # pragma: no cover
    try:
        src = os.path.join(root_dir(), filename)
        # Figure out how flask returns static files
        # Tried:
        # - render_template
        # - send_file
        # This should not be so non-obvious
        return open(src).read()
    except IOError as exc:
        return str(exc)

@application.route("/")
def test_page():
    content = get_file('index.html')
    return Response(content, mimetype="text/html")

if __name__ == "__main__":
    application.run()
