from pod_bot import PodBot
from flask import Flask
application = Flask(__name__)

@application.route("/")
def status_page():
    retStr =  "<h>Pod Status Page</h>"
    retStr +=  "<h2><a href='/config'>Configuration</a></h2>"
    bot = PodBot()
    bot.about()
    return retStr

@application.route("/config")
def config_page():
    return "OpenShift URL: " + os.environ["OPENSHIFT_URL"]

if __name__ == "__main__":
    application.run()
