from pod_bot import PodBot
from flask import Flask
application = Flask(__name__)

@application.route("/")
def status_page():
    print ("<h>Pod Status Page</h>")
    print ("<h2><a href='/config'>Configuration</a></h2>")
    bot = PodBot()
    bot.about()
    return bot.about()

@application.route("/config")
def config_page():
    println ("OpenShift URL: " + os.environ["OPENSHIFT_URL"])

if __name__ == "__main__":
    application.run()
