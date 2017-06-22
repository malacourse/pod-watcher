#!/usr/bin/python2.7

import datetime
import time
import re
import sys
import os
import pickle
import logging
import json
import threading as thread
import ssl
import traceback
import websocket
import urllib

class PodBot(object):

    def __init__(self):
        self.osURL = "localhost:8443/api/v1/namespaces/test"
        self.osToken = "QqFVOYew09aAbfnUhlzq2QoyVmYG1OBKkxp_3yUIOgs"
        self.filePath = "/var/lib/podstatus/pod_status.txt"
        self.logger = logging.getLogger(__name__)
        self.logger.info("START")
        if "OPENSHIFT_URL" in os.environ:
           self.osURL = os.environ["OPENSHIFT_URL"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]
        if "STATUSFILE" in os.environ:
           sefl.filePath = os.environ["STATUSFILE"]
        self.podStatus = {}

    def on_message(self, ws, message):
        self.logger.debug(message)
        parsed_json = json.loads(message)
        self.parse_json(parsed_json)
        self.save_status()

    def on_error(self, ws, error):
        self.logger.error (error)

    def on_close(self, ws):
        self.logger.info ("### closed:" + str(self.myThread.is_alive()))
        os._exit(2)

    def about(self):
       self.logger.info ("pod bot status module")
      
    def runSocket(self,url):
        def run(url):
                time.sleep(1)
                #url = urllib.pathname2url(url)
                self.logger.info("URL" + url)
                self.ws = websocket.WebSocketApp(url, on_message = self.on_message, on_error = self.on_error, on_close=self.on_close)
                #ws.on_open = self.on_open
                self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                self.logger.warn("thread terminating...")
                
        args = [url]
        #self.myThread = thread.start_new_thread(run, tuple(args))
        self.myThread = thread.Thread(target=run, args=[url,])
        self.myThread.start()
        self.logger.info("Thread startup complete:" + str(self.myThread))
        
    
    def save_status(self):
        # save to file:
        with open(self.filePath, 'wb') as f:
            pickle.dump(self.podStatus, f)
            f.close()


    def start(self):
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
            self.runSocket(url)
            self.logger.info("Monitor startup complete")

            #while True:
            #    self.logger.debug("Running forever!")
            #ws = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})
            
        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())
 
    def get_status(self):
        # load from file:
        with open('/tmp/pod_status.txt', 'r') as f:
            try:
                data = pickle.load(f)
            except ValueError:
                data = {}
        return data


    def parse_json(self, json):
        self.logger.info("json:" + str(json.__class__))
        
        status = json["object"]["status"]
        #meta = json["object"]["metadata"]
        #spec = json["object"]["spec"]
        #self.logger.info("status:" + str(status))
        #self.logger.info("meta:" + str(meta))
        #self.logger.info("spec:" + str(spec))
        self.logger.error("STATUS:" + str(status.__class__))
        if type(status) is dict:
            contStatus = status["containerStatuses"]
            #conditions = status["conditions"]
            self.logger.info("name:" + contStatus[0]["name"])
            self.logger.info("image:" + contStatus[0]["image"])
            if "ose-" not in contStatus[0]["image"]:
                self.logger.info("Not OSI Image")
                self.logger.info("contStatus:" + str(contStatus[0]))
                #podstatus = PodStatus(contStatus[0]["name"], contStatus[0]["image"],contStatus[0]["restartCount"])
                ps = {}
                ps["state"] = contStatus[0]["state"]
                ps["restartCount"] = contStatus[0]["restartCount"]
                self.podStatus[contStatus[0]["name"]] = ps
        else:
            self.logger.warn("Status is not type Dictionary!")
