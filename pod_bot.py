#!/usr/bin/python2.7

import datetime
import time
import re
import sys
import os
import logging
import json
import ssl
import traceback
import websocket
import thread

from flask import Flask
application = Flask(__name__)

@application.route("/")
def hello():
    return "Hello World!"


class PodBot(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def on_message(self, ws, message):
        print message

    def on_error(self, ws, error):
        print error

    def on_close(self, ws):
        print "### closed ###"

    def on_open(self, ws):
        def run(*args):
            for i in range(3):
                time.sleep(1)
                ws.send("Hello %d" % i)
            time.sleep(1)
            ws.close()
            print "thread terminating..."
        thread.start_new_thread(run, ())

    def main(self):
        try:
            # Set up logging
            log_fmt = '%(asctime)-15s %(levelname)-8s %(message)s'
            log_level = logging.INFO
            #log_level = logging.DEBUG

            if "GITBASHTTY" in os.environ:
                logging.basicConfig(format=log_fmt, level=log_level)
            else:
                if sys.stdout.isatty():
                    # Connected to a real terminal - log to stdout
                    logging.basicConfig(format=log_fmt, level=log_level)
                else:
                    # Background mode - log to file
                    logging.basicConfig(format=log_fmt, level=log_level, filename='test.log')

            # Banner
            self.logger.info("==========================================================")
            self.logger.info( "Starting Pod Bot")

            #sslopt={"cert_reqs": ssl.CERT_NONE},
            #websocket.enableTrace(True)
            url="wss://ose-dev-cnsl.divbiz.net:8443/api/v1/namespaces/redhat-sandbox/pods?watch=true&access_token=ADD-CONSOLE-TOKEN-HERE"
            #ws = websocket.WebSocketApp(url, on_message = self.on_message, on_error = self.on_error, on_close = self.on_close)
            #ws.on_open = self.on_open
            #ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

            #Create a socket and listen for tickles
            ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
            while True:
                result = ws.recv()
                print"Received '%s'" % result
                #parsed_json = json.loads(result)
                #stocket_type = parsed_json['type']


        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())

if __name__ == "__main__":
    application.run()

