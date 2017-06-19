from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    print"start hello"
    bot = PodBot()
    bot.about()
    return "Hello New World!"

if __name__ == "__main__":
    application.run()
