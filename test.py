#!/usr/bin/python2.7

import datetime
import time
import re
import sys
import os
import logging
import json
import thread
import ssl
import traceback
import websocket
from pod_status import PodStatus

class PodBot(object):


    def __init__(self):
        print("Bot INIT START")
        self.osURL = "localhost:8443/api/v1/namespaces/test"
        self.osToken = "yCEDk4pYRumrCi9hovUdDtcRN_XmkAWv3HGHFClbQmg"

        self.logger = logging.getLogger(__name__)
        if "OPENSHIFT_URL" in os.environ:
           self.osURL = os.environ["OPENSHIFT_URL"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]
        self.podStatus = {}

    def on_message(self, ws, message):
        print (message)

    def on_error(self, ws, error):
        print (error)

    def on_close(self, ws):
        print ("### closed ###")

    def about(self):
       print ("pod bot status module")
      
    def runSocket(self,url):
        def run(url):
            ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})

            nTries = 0
            while nTries < 100000:
                result = ws.recv()
                self.logger.info("Received '%s'" % result)
                parsed_json = json.loads(result)
                self.parse_json(parsed_json)
                #self.logger.warn("JSON: " + str(parsed_json))
                #stocket_type = parsed_json['type']
                nTries = nTries + 1
                time.sleep(10)

            print "thread terminating..."
        args = [url]
        thread.start_new_thread(run, tuple(args))

    def get_status(self):
        result = "Error"
        try:
            # Set up logging
            log_fmt = '%(asctime)-15s %(levelname)-8s %(message)s'
            log_level = logging.WARN

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
            #ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
            
            self.runSocket(url)

            nTries = 0
            while nTries < 100000:
            #    result = ws.recv()
            #    self.logger.debug("Received '%s'" % result)
            #    parsed_json = json.loads(result)
            #    self.parse_json(parsed_json)
            #    #self.logger.warn("JSON: " + str(parsed_json))
            #    #stocket_type = parsed_json['type']
            #    nTries = nTries + 1
                print("hello:" + str(self.podStatus))
                time.sleep(10)           

        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())

    def parse_json(self, json):
        print("json:" + str(json.__class__))
        status = json["object"]["status"]
        meta = json["object"]["metadata"]
        spec = json["object"]["spec"]
        #print("status:" + str(status))
        #print("meta:" + str(meta))
        #print("spec:" + str(spec))
        contStatus = status["containerStatuses"]
        conditions = status["conditions"]
        #print("cs:" + str(contStatus))
        #print("cond:" + str(conditions))
        #for key, val in contStatus[0].iteritems():
        #    print("key:" + str(key))
        #    print("items:" + str(val.__class__))
        print("name:" + contStatus[0]["name"])
        print("image:" + contStatus[0]["image"])
        if "ose-" not in contStatus[0]["image"]:
            print("Not OSI Image")
            print("contStatus:" + str(contStatus[0]))
            podstatus = PodStatus(contStatus[0]["name"], contStatus[0]["image"],contStatus[0]["restartCount"])
            self.podStatus[contStatus[0]["name"]] = podstatus




 
if __name__ == "__main__":
    PodBot().get_status()
