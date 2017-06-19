from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    return "This is the Pod watcher server!"

if __name__ == "__main__":
    application.run(port=8070)
