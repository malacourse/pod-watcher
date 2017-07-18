#!/usr/bin/python2.7

import datetime
import time
import re
import pytz
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
        self.osToken = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJ0ZXN0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InBvZHdhdGNoZXJzYS10b2tlbi03ZjNnMyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJwb2R3YXRjaGVyc2EiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJiMDg5YzRhYS02YjFlLTExZTctYjdiOC0wODAwMjdlYTczYzciLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6dGVzdDpwb2R3YXRjaGVyc2EifQ.N_bYQs-Pg_1xpDg2M66xI4TM5ag2AOVYipgUBPptT6Z3qbR0q3RPyJVyTVnAvSFBhg2_kUT4WGGKi6qXzCwRBfXo_Yu_WCL4P-dTlZ0dd0OBNh-kbgPnSfsi0_j9lRBHtm-NH7BB037SiKLuzDY6A0q3QoUnUhzJDgLp9h3ci33CaXwLPUdFFHXhL0xj5yfahLyInCJL1jCK1vgylpynhDqEoeO4keOmA7OhEN6s1cdN6dDbTvr8leky1AKuIQYWJY_ieskULgusfvR99sRSKIBFklLQ1UXdLsmVFOXTdvc3HeO04B0kHsQminasJEFJ-0-v81DZkPq-Mt1O7lfMRA"
        self.filePath = "/var/lib/podstatus/pod_status.txt"
        self.logger = logging.getLogger(__name__)
        self.threshold = 5
        self.log_level = logging.INFO
        self.timeframe = timedelta(hours=4)
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
           self.timeframe = timedelta(minutes=configMinutes)
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

    local_tz = pytz.timezone('America/New_York')
    def utc_to_local(self, utc_dt):
        self.logger.debug("UTC TIME:" + str(utc_dt))
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(self.local_tz)
        self.logger.debug("UTC NEW TIME:" + str(local_dt))
        return self.local_tz.normalize(local_dt).strftime(self.dateTimeFormat)

    def remove_old_restarts(self, currentList):
        newList = []
        today = datetime.now()
        self.logger.debug("DELTA:" + str(self.timeframe))
        for strTime in currentList:
            rs_dt = datetime.strptime(strTime,self.dateTimeFormat)            
            if rs_dt >= today - self.timeframe:
               newList.append(strTime)
        return newList
 
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
            self.logger.info("Openshift Host:" + self.osHost)
            self.logger.info("Openshift Token:" + self.osToken)
            self.logger.info("Openshift Namespace:" + self.osNs)
            self.logger.info("==========================================================")

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
            self.logger.warn("Status file empty!")
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
                msgType = str(json["type"])
                self.logger.info("contStatus:" + str(contStatus[0]) + ", TYPE:" + msgType)
                self.logger.debug("Msg:" + str(json))
                ps = {}
                podStatus = self.get_status()
                
                totalRestartCount = int(contStatus[0]["restartCount"])
                baseRestartCount = 0
                newItem = True
                podName = contStatus[0]["name"]
                if podName in podStatus:
                  ps = podStatus[podName]
                if msgType == "ADDED":
                    baseRestartCount = totalRestartCount
                    ps["alertStatus"] = "None"
                    ps["podName"] = podName
                    ps["state"] = contStatus[0]["state"]
                    if "startTime" in status:
                        ps["startTime"] = status["startTime"]
                    else:
                        ps["startTime"] = ""
                    baseRestartCount = totalRestartCount
                    ps["restarts"] = []
                else:
                    if msgType == "DELETED":
                      ps["restarts"] = []
                    else:
                        restartTime = datetime.now().strftime(self.dateTimeFormat)
                        if "running" in contStatus[0]["state"]:
                            restartTime = contStatus[0]["state"]["running"]["startedAt"]
			    utcTime = datetime.strptime(restartTime,self.dateTimeFormat)
                            restartTime = self.utc_to_local(utcTime)
                        if "terminated" in contStatus[0]["state"]:
                           restartTime = contStatus[0]["state"]["terminated"]["startedAt"]
                           utcTime = datetime.strptime(restartTime,self.dateTimeFormat)
                           restartTime = self.utc_to_local(utcTime)
                        
                        ps["restarts"].append(restartTime)

                if "terminated" in contStatus[0]["state"]:
                    ps["alertStatus"] = "Warn"
                if "waiting" in contStatus[0]["state"] and contStatus[0]["state"]["waiting"]["reason"] == "CrashLoopBackOff":
                    ps["alertStatus"] = "Warn"

                ps["totalRestartCount"] = totalRestartCount
                ps["lastUpdateTime"] =  datetime.now().strftime(self.dateTimeFormat)

                self.logger.info("Total reset count:" + str(totalRestartCount))
                self.logger.info("Recent Restart count:" + str(baseRestartCount))
                                
                if ps["alertStatus"] != "Warn":
                    ps["restarts"] = self.remove_old_restarts(ps["restarts"])
                ps["currentRestarts"] = len(ps["restarts"])
                self.logger.debug("Current reset count:" + str(ps["currentRestarts"]))
                if len(ps["restarts"]) >= self.threshold:
                    self.logger.warn("Theshold exceeded:" + str(self.threshold)) 
                    ps["alertStatus"] = "Warn"
                podStatus[ps["podName"]] = ps
                self.save_status(podStatus)

        else:
            self.logger.warn("Status is not type Dictionary!")
