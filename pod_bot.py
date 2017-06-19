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


    def __init__(self):
        print("Bot INIT START")
        self.osURL = "ose-dev-cnsl.divbiz.net:8443/api/v1/namespaces/redhat-sandbox"
        self.osToken = "TOKEN-A"

        self.logger = logging.getLogger(__name__)
        if "OPENSHIFT_URL" in os.environ:
           self.osURL = os.environ["OPENSHIFT_URL"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]

    def on_message(self, ws, message):
        print (message)

    def on_error(self, ws, error):
        print (error)

    def on_close(self, ws):
        print ("### closed ###")

    def about(self):
       print ("pod bot status module")
    
    def get_status(self):
        result = "Error"
        try:
            # Set up logging
            log_fmt = '%(asctime)-15s %(levelname)-8s %(message)s'
            log_level = logging.INFO

            logging.basicConfig(format=log_fmt, level=log_level)

            # Banner
            self.logger.info("==========================================================")
            self.logger.info( "Starting Pod Bot")

            #sslopt={"cert_reqs": ssl.CERT_NONE},
            #websocket.enableTrace(True)
            url="wss://" + self.osURL + "/pods?watch=true&access_token=" + self.osToken
            #ws = websocket.WebSocketApp(url, on_message = self.on_message, on_error = self.on_error, on_close = self.on_close)
            #ws.on_open = self.on_open
            #ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

            #Create a socket and listen for tickles
            self.logger.info("Calling websocket with:" + url)
            ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
            
            result = ws.recv()
            self.logger.info("Received '%s'" % result)
                #parsed_json = json.loads(result)
                #stocket_type = parsed_json['type']
           
            return result

        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())

