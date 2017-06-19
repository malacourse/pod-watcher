from pod_bot import PodBot
from flask import Flask
import os
application = Flask(__name__)

@application.route("/")
def status_page():
    retStr =  "<h1>Pod Status Page</h1>"
    retStr +=  "<h2><a href='/config'>Configuration</a></h2>"
    bot = PodBot()
    bot.about()
    return retStr

@application.route("/config")
def config_page():
    retStr = "OpenShift URL: " + os.environ["OPENSHIFT_URL"] 
    return retStr

if __name__ == "__main__":
    application.run()
