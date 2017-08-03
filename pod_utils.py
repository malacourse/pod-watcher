#!/usr/bin/python2.7

import datetime
import time
from pytz import utc, timezone
import sys
import os
import pickle
import logging
import json
import traceback
import websocket
from datetime import datetime, timedelta
import requests

class PodUtils(object):

    def __init__(self):
        self.osHost = "192.168.99.101:8443"
        self.osToken = ""
        self.secretPath = "/etc/secret"
        self.filePath = "/var/tmp/"
        self.logger = logging.getLogger(__name__)
        self.log_level = logging.INFO
        ## "2017-06-28T18:30:55Z"
        self.dateTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
        self.displayTimeFormat = "%m/%d/%Y-%H:%M:%S"
        
        if "OPENSHIFT_HOST" in os.environ:
           self.osHost = os.environ["OPENSHIFT_HOST"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]
        else:
            token = self.load_token_from_secret()
            if token != "":
                self.osToken = token

        if "PODMONITOR_FILEPATH" in os.environ:
           self.filePath = os.environ["PODMONITOR_FILEPATH"]
        if "PODMONITOR_LOGLEVEL" in os.environ:
           configLevel = os.environ["PODMONITOR_LOGLEVEL"]
           if configLevel == "WARN": self.log_level = logging.WARN
           if configLevel == "DEBUG": self.log_level = logging.DEBUG
           if configLevel == "ERROR": self.log_level = logging.ERROR

    def get_token(self):
       return self.osToken
      
    def get_host(self):
       return self.osHost

    def get_namespaces(self): 
        ns = ""
        if "OPENSHIFT_NAMESPACE" in os.environ:
           return os.environ["OPENSHIFT_NAMESPACE"]

        try: 
           url = "https://" + self.osHost + "/oapi/v1/projects/" 
           headers = {"Authorization" : "Bearer " + self.osToken} 
           self.logger.info("URL:" + url) 
           self.logger.debug("Header:" + str(headers)) 
           retStatus = requests.get(url, headers=headers, verify=False) 
           if isinstance(retStatus.content,bytes): 
              self.logger.info("Ret Type is Bytes") 
              strNs = retStatus.content.decode("utf-8") 
           else: 
              strNs = str(retStatus.content) 

           nsJson = json.loads(strNs)
           if "items" in nsJson:
              for item in nsJson["items"]:
                 nsName = item["metadata"]["name"]
                 if len(ns) > 0:
                    ns = ns + "," 
                 ns = ns +  nsName
        except Exception as ex: 
           self.logger.error(str(ex))
        self.logger.info("Retrieved Namespace list:" + ns)
        return ns 

    local_tz = timezone('America/New_York')
    def utc_to_local(self, utc_dt, dtFormat):
        self.logger.debug("UTC TIME:" + str(utc_dt))
        local_dt = utc_dt.replace(tzinfo=utc).astimezone(self.local_tz)
        self.logger.debug("UTC NEW TIME:" + str(local_dt))
        return self.local_tz.normalize(local_dt).strftime(dtFormat)

    def save_status(self,podStatus,namespace):
        # save to file:
        podList = []
        try:
            if isinstance(podStatus,list):
               podList = podStatus
            else:
               for key, ps in podStatus.items():
                  podList.append(ps)
            with open(self.filePath + namespace, 'wb') as f:
                pickle.dump(podList, f)
                f.close()
        except:
            self.logger.error("%s", traceback.format_exc())
            self.logger.error("Error Saving Status")

    def get_status_for_ns(self, namespace):
        # load from file:
        try:
            with open(self.filePath + namespace, 'rb') as f:
                data = pickle.load(f)
                data = self.format_restart_times(data)
        except:
                data = []
        self.logger.debug("Data:" + str(data))
        return data

    def format_restart_times(self,pods):
       for pod in pods:
          formatedRestarts = []
          restarts = pod["restarts"]
          if len(restarts) > 0:
             for strTime in restarts:
                utcTime = datetime.strptime(strTime,self.dateTimeFormat)
                localTime = self.utc_to_local(utcTime,self.displayTimeFormat)
                formatedRestarts.append(localTime)
          pod["restartsLocal"] = formatedRestarts
       return pods

    def get_status_list(self,namespace):
        # load from file:
        try:
            with open(self.filePath + namespace, 'rb') as f:
                data = pickle.load(f)
                data = self.format_restart_times(data)
        except:
                self.logger.error("%s", traceback.format_exc())
                data = []
        self.logger.debug("Data:" + str(data))
        return data

    def load_token_from_secret(self):
        retToken = ""
        try:
            with open(self.secretPath + "/token", 'rb') as f:
                retToken = f.read()
                if isinstance(retToken,bytes):
                  retToken = retToken.decode("utf-8")
        except:
            self.logger.warn("No service account secret mounted!")
        self.logger.debug("Read Token:" + retToken)
        return retToken.rstrip()
 
    def get_status(self,namespace):
        # load from file:
        data = {}
        try:
            with open(self.filePath + namespace, 'rb') as f:
                saveddata = pickle.load(f)
                if type(saveddata) == list:
                    for ps in saveddata:
                        data[ps["podName"]] = ps   
        except:
            self.logger.warn("Status file empty!")
            data = {}

        self.logger.debug("Loaded data:" + str(data))
        return data
