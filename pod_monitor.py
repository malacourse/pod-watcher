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
from datetime import datetime, timedelta

class PodMonitor(object):

    def __init__(self):
        self.osHost = "192.168.99.100:8443"
        self.osNs = "test"
        self.osToken = "2ry4PaE0XNlCd0Po1YPMC3JdYxPlOOLIS_6TFOwNRLA"
        self.filePath = "/var/lib/podstatus/pod_status.txt"
        self.logger = logging.getLogger(__name__)
        self.threshold = 5
        self.log_level = logging.INFO
        self.timeframe = timedelta(hours=12)
        ## "2017-06-28T18:30:55Z"
        self.dateTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
        if "OPENSHIFT_HOST" in os.environ:
           self.osHost = os.environ["OPENSHIFT_HOST"]
        if "OPENSHIFT_NAMESPACE" in os.environ:
           self.osNs = os.environ["OPENSHIFT_NAMESPACE"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]
        if "STATUSFILE" in os.environ:
           self.filePath = os.environ["STATUSFILE"]
        if "RESTART_THRESHOLD" in os.environ:
           self.threshold = int(os.environ["RESTART_THRESHOLD"])
        if "RESTART_TIMEFRAME" in os.environ:
           configMinutes = int(os.environ["RESTART_TIMEFRAME"])
           self.timeframe = timedelta(minutes=confMinutes)
        if "PODMONITOR_LOGLEVEL" in os.environ:
           configLevel = os.environ["PODMONITOR_LOGLEVEL"]
           if configLevel == "WARN": self.log_level = logging.WARN
           if configLevel == "DEBUG": self.log_level = logging.DEBUG
           if configLevel == "ERROR": self.log_level = logging.ERROR

    def on_message(self, ws, message):
        self.logger.debug(message)
        parsed_json = json.loads(message)
        self.parse_json(parsed_json)

    def on_error(self, ws, error):
        self.logger.info (error)

    def on_close(self, ws):
        self.logger.info ("### closed ###")
        os._exit(-1)

    def about(self):
       self.logger.info ("pod bot status module")
      

    def runSocket(self,url):
        def run(url):
                self.logger.info("Thread start: " + url)
                header = {"Authorization: Bearer " + self.osToken}
                ws = websocket.WebSocketApp(url, header=header,on_message = self.on_message, on_error = self.on_error, on_close = self.on_close)
                #ws.on_open = self.on_open
                ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                #while True:
                #    self.logger.debug("After run...")
        args = [url]
        #thread.start_new_thread(run, tuple(args))
        self.logger.info("Starting thread ...")
        t = thread.Thread(target=run, args=(url,))
        t.start()
        self.logger.info("Thread started!")
 
    def save_status(self,podStatus):
        # save to file:
        podList = []
        try:
            for key, ps in podStatus.items():
               podList.append(ps)
        
            with open(self.filePath, 'wb') as f:
                pickle.dump(podList, f)
                f.close()
        except:
            self.logger.error("Error Saving Status")

    def start(self):
        result = "Error"
        try:
            # Set up logging
            log_fmt = '%(asctime)-15s %(levelname)-8s %(message)s'

            logging.basicConfig(format=log_fmt, level=self.log_level)

            # Banner
            self.logger.info("==========================================================")
            self.logger.info( "Starting Pod Bot")
            self.logger.info("Current Log Level:" + str(self.log_level))
            self.logger.info("Restart Timeframe:" + str(self.timeframe))
            self.logger.info("Restart Threshold:" + str(self.threshold))

            url="wss://" + self.osHost + "/api/v1/namespaces/" + self.osNs + "/pods?watch=true"
            ##&access_token=" + self.osToken

            self.runSocket(url)
            
        except KeyboardInterrupt:
            logging.critical("Terminating due to keyboard interrupt")
        except:
            logging.critical("Terminating due to unexpected error: %s", sys.exc_info()[0])
            logging.critical("%s", traceback.format_exc())
 
    def get_status(self):
        # load from file:
        data = {}
        try:
            with open(self.filePath, 'rb') as f:
                saveddata = pickle.load(f)
                if type(saveddata) == list:
                    for ps in saveddata:
                        data[ps["podName"]] = ps   
        except:
            self.logger.error("Error reading Status")
            data = {}

        self.logger.debug("Loaded data:" + str(data))
        return data


    def parse_json(self, json):
        self.logger.debug("json:" + str(json))
        
        status = json["object"]["status"]
        self.logger.debug("STATUS:" + str(status.__class__))
        if type(status) is dict:
            contStatus = status["containerStatuses"]
            #conditions = status["conditions"]
            #self.logger.info("name:" + contStatus[0]["name"])
            if "ose-" not in contStatus[0]["image"]:
                self.logger.info("contStatus:" + str(contStatus[0]))
                ps = {}
                podStatus = self.get_status()
                
                ps["podName"] = contStatus[0]["name"]
                ps["state"] = contStatus[0]["state"]
                ps["restartCount"] = contStatus[0]["restartCount"]
                ps["lastUpdateTime"] =  datetime.now().strftime(self.dateTimeFormat)
                restartCount = int(contStatus[0]["restartCount"])
                alertedCount = 0

                #don't keep sending alerts if already notified
                if ps["podName"] in podStatus:
                    self.logger.debug("Existing Pod Data:" + str(podStatus[ps["podName"]]))
                    alertStatus = podStatus[ps["podName"]]["alertStatus"]
                    ps["alertStatus"] = alertStatus
                    alertedCount = int(podStatus[ps["podName"]]["alertedAtCount"])
                    if alertStatus == "Sent":
                        self.logger.debug("Current status is Sent")
                        if alertedCount <= restartCount:
                            restartCount = restartCount - alertedCount
                else:
                    ps["alertStatus"] = "None"
                self.logger.debug("Current reset count:" + str(restartCount))
                self.logger.debug("AlertedAt count:" + str(alertedCount))
                
                ps["alertedAtCount"] = alertedCount
                self.logger.debug("Current reset count:" + str(restartCount))
                if restartCount > self.threshold:
                    self.logger.warn("Theshold exceeded:" + str(self.threshold)) 
                    ps["alertStatus"] = "Warn"
                podStatus[ps["podName"]] = ps
                self.save_status(podStatus)

        else:
            self.logger.warn("Status is not type Dictionary!")
