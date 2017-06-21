#!/usr/bin/python2.7

import datetime
import time
import re
import sys
import os
import logging
import json
import _thread
import ssl
import traceback
import websocket
from pod_status import PodStatus

class PodBot(object):


    def __init__(self):
        self.osURL = "localhost:8443/api/v1/namespaces/test"
        self.osToken = "yCEDk4pYRumrCi9hovUdDtcRN_XmkAWv3HGHFClbQmg"

        self.logger = logging.getLogger(__name__)
        if "OPENSHIFT_URL" in os.environ:
           self.osURL = os.environ["OPENSHIFT_URL"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]
        self.podStatus = {}
        self.get_status()

    def on_message(self, ws, message):
        self.logger.info (message)

    def on_error(self, ws, error):
        self.logger.info (error)

    def on_close(self, ws):
        self.logger.info ("### closed ###")

    def about(self):
       self.logger.info ("pod bot status module")
      
    def runSocket(self,url):
        def run(url):
            ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})

            nTries = 0
            while nTries < 100000:
                result = ws.recv()
                self.logger.debug("Received '%s'" % result)
                parsed_json = json.loads(result)
                self.parse_json(parsed_json)
                #self.logger.warn("JSON: " + str(parsed_json))
                #stocket_type = parsed_json['type']
                nTries = nTries + 1
                time.sleep(10)

            self.logging.info("thread terminating...")
        args = [url]
        _thread.start_new_thread(run, tuple(args))

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
            #ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
            
            self.runSocket(url)

            nTries = 0
            #while nTries < 100000:
            #    result = ws.recv()
            #    self.logger.debug("Received '%s'" % result)
            #    parsed_json = json.loads(result)
            #    self.parse_json(parsed_json)
            #    #self.logger.warn("JSON: " + str(parsed_json))
            #    #stocket_type = parsed_json['type']
            #    nTries = nTries + 1
            #    self.logger.info("hello:" + str(self.podStatus))
            #    time.sleep(10)           

        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())

    def parse_json(self, json):
        self.logger.info("json:" + str(json.__class__))
        status = json["object"]["status"]
        meta = json["object"]["metadata"]
        spec = json["object"]["spec"]
        #self.logger.info("status:" + str(status))
        #self.logger.info("meta:" + str(meta))
        #self.logger.info("spec:" + str(spec))
        contStatus = status["containerStatuses"]
        conditions = status["conditions"]
        #self.logger.info("cs:" + str(contStatus))
        #self.logger.info("cond:" + str(conditions))
        #for key, val in contStatus[0].iteritems():
        #    self.logger.info("key:" + str(key))
        #    self.logger.info("items:" + str(val.__class__))
        self.logger.info("name:" + contStatus[0]["name"])
        self.logger.info("image:" + contStatus[0]["image"])
        if "ose-" not in contStatus[0]["image"]:
            self.logger.info("Not OSI Image")
            self.logger.info("contStatus:" + str(contStatus[0]))
            podstatus = PodStatus(contStatus[0]["name"], contStatus[0]["image"],contStatus[0]["restartCount"])
            self.podStatus[contStatus[0]["name"]] = podstatus

    def start():
        bot = PodBot().get_status()
