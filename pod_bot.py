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

class PodBot(object):

    _osURL = "ose-dev-cnsl.divbiz.net:8443/api/v1/namespaces/redhat-sandbox"
    _osToken = "TOKEN-A"

    def __init__(self):
        print("Bot INIT START")
        self.logger = logging.getLogger(__name__)
        if "OPENSHIFT_URL" in os.environ:
           _osURL = os.environ["OPENSHIFT_URL"]
        if "OPENSHIFT_TOKEN" in os.environ:
           _osToken = os.environ["OPENSHIFT_TOKEN"]

    def on_message(self, ws, message):
        print (message)

    def on_error(self, ws, error):
        print (error)

    def on_close(self, ws):
        print ("### closed ###")

    def about(self):
       print ("pod bot status module")
    
    def get_status():
        print("get status start")
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
            url="wss://" + osURL + "/pods?watch=true&access_token=" + osToken
            #ws = websocket.WebSocketApp(url, on_message = self.on_message, on_error = self.on_error, on_close = self.on_close)
            #ws.on_open = self.on_open
            #ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

            #Create a socket and listen for tickles
            print("Calling websocket with:" + url)
            ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
            while True:
                result = ws.recv()
                print ("Received '%s'" % result)
                #parsed_json = json.loads(result)
                #stocket_type = parsed_json['type']
           
            return result

        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())

