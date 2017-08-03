from pod_monitor import PodMonitor
from flask import Flask, Response
from pod_status_reader import PodStatusReader
import os
import sys
import traceback
import json
from pod_utils import PodUtils

monitor = PodMonitor().start()
application = Flask(__name__)
utils = PodUtils()

def get_current_config():
    threshold = 5
    configMinutes = 240
    pageRefreshSeconds = 60
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
    if "PM_PAGEREFERSH_SECONDS" in os.environ:
        pageRefreshSeconds = int(os.environ["PM_PAGEREFRESH_SECONDS"])
    config["pageRefreshSeconds"] = pageRefreshSeconds
    config["timeframe"] = configMinutes
    config["threshold"] = threshold
    return config

def get_namespaces_list(namespaces):
    ret = []
    if "," in namespaces:
       ret = namespaces.split(",")
    else:
       ret = [namespaces]
    return ret

@application.route("/status")
def status_service():
    threshold = 3
    if "RESTART_THRESHOLD" in os.environ:
           threshold = int(os.environ["RESTART_THRESHOLD"])
    namespaces = utils.get_namespaces()

    nslist = get_namespaces_list(namespaces)
    config = get_current_config()
    status = '{"status" : "None"}'
    try:
       nCount = 0
       for namespace in nslist:
          items = utils.get_status_list(namespace)
          if type(items) == list:
              if nCount == 0:
                 status = '{"config" :'  + json.dumps(config) + ',"namespaces" :['
              else:
                 status = status + ','
              status += '{"namespace" : "' + namespace + '", "pods" : ' + json.dumps(items) + '}'
          nCount = nCount + 1
       if nCount > 0:
          status += ']}'
       
       return status
    except:
       print(traceback.format_exc())
       status = "Error:" + str(traceback.format_exc())
    return status
    
@application.route("/pod-restart-alerts")
def restart_alerts():
    threshold = 5
    if "RESTART_THRESHOLD" in os.environ:
           threshold = int(os.environ["RESTART_THRESHOLD"])
    namespaces = utils.get_namespaces()

    nslist = get_namespaces_list(namespaces)
    status = '{"status" : "None"}'
    try:
       status = PodStatusReader().get_alerts(nslist)
    except:
       print(traceback.format_exc())
       status = '{"status" : "Pod Monitor Error"}'
    return status

@application.route("/events/<namespace>")
@application.route("/events/<namespace>/<podname>")
def get_events(namespace,podname="None"):
    status = '{"events" : "None"}'
    try:
       status = json.dumps(PodStatusReader().get_events(namespace,podname)) 
    except:
       print(traceback.format_exc())
       status = '{"events" : "Pod Monitor Error"}'
    return status

@application.route("/pods/<namespace>")
@application.route("/pods/<namespace>/<podname>")
def get_pods(namespace,podname="None"):
    status = '{"pods" : "None"}'
    try:
       status = json.dumps(PodStatusReader().get_pods(namespace,podname))
    except:
       print(traceback.format_exc())
       status = '{"pods" : "Pod Monitor Error"}'
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
