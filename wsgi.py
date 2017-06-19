import pod_bot

from flask import Flask
application = Flask(__name__)

@application.route("/")
def status_page():
    print ("Start status page")
    bot = PodBot()
    bot.about()
    return bot.about()

if __name__ == "__main__":
    application.run()
