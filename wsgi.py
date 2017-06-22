from pod_bot import PodBot
from flask import Flask, Response
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
           for key, ps in items.items():
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

@application.route("/index")
def test_page():
    content = get_file('index.html')
    print("content:" + content)
    return Response(content, mimetype="text/html")

@application.route("/config")
def config_page():
    retStr = "<table><tr><td>Name</td><td></tr>"
    if "OPENSHIFT_HOST" in os.environ:
        retStr += "<tr><td>OPENSHIFT_HOST</td><td>" + os.environ["OPENSHIFT_HOST"] + "</td></tr>"
    if "OPENSHIFT_NAMESPACE" in os.environ:
        retStr += "<tr><td>OPENSHIFT_NAMESPACE</td><td>" + os.environ["OPENSHIFT_NAMESPACE"] + "</td></tr>"
    if "OPENSHIFT_TOKEN" in os.environ:
        retStr += "<tr><td>OPENSHIFT_TOKEN</td><td>" + os.environ["OPENSHIFT_TOKEN"] + "</td></tr>"
    if "OPENSHIFT_THRESHOLD" in os.environ:
        retStr += "<tr><td>THRESHOLD</td><td>" + os.environ["THRESHOLD"] + "</td></tr>"
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

if __name__ == "__main__":
    application.run()
