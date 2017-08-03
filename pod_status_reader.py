#!/usr/bin/python2.7
import logging
import pickle
import os
import json
import requests
from datetime import datetime, timedelta
from pytz import utc, timezone
from pod_utils import PodUtils

class PodStatusReader():

    def __init__(self,namespace="None"):
        self.utils = PodUtils()
        self.namespace = namespace
        self.logger = logging.getLogger(__name__)
        self.osHost = ""
        self.osToken = self.utils.get_token()
        self.logger = logging.getLogger(__name__)
        self.log_level = logging.INFO
        ## "2017-06-28T18:30:55Z"
        self.dateTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
        self.displayTimeFormat = "%m/%d/%Y-%H:%M:%S"
        self.osHost = self.utils.get_host()
        self.includeEvents = True
        if "PODMONITOR_INCLUDE_EVENTS" in os.environ:
           self.includeEvents = os.environ["PODMONITOR_INCLUDE_EVENTS"].lower() == "true"
 
    def get_alerts(self,namespaces):
        retStatus = []
        for namespace in namespaces:
           status = self.utils.get_status_for_ns(namespace)
           for ps in status:
              if ps["alertStatus"] == "Warning" or ps["alertStatus"] == "Failure":
                 newPs = dict(ps)
                 if self.includeEvents == True:
                    newPs["Events"] = self.get_events(namespace,newPs["podLongName"])
                 retStatus.append(newPs)
                 ps["alertStatus"] = "Sent"
                 ps["restarts"] = []
                 ps["currentRestarts"] = 0

           if len(retStatus) > 0:
               self.logger.info("Reported alerts")
               self.utils.save_status(status,namespace)
        return json.dumps(retStatus)
             
    def get_pods(self,namespace,podname="None"):
        pods = []
        try:
           url = "https://" + self.osHost + "/api/v1/namespaces/" + namespace + "/pods"
           headers = {"Authorization" : "Bearer " + self.osToken}
           self.logger.info("URL:" + url)
           self.logger.debug("Header:" + str(headers))
           retStatus = requests.get(url, headers=headers, verify=False)
           if isinstance(retStatus.content,bytes):
              self.logger.info("Ret Type is Bytes")
              strPods = retStatus.content.decode("utf-8")
           else:
              strPods = str(retStatus.content)

           nsPods = json.loads(strPods)
           if podname != "None":
             for pod in nsPods["items"]:
                if podname == pod["metadata"]["name"]:
                    pods.append(pod)
           else:
              pods = nsPods
        except Exception as ex:
           self.logger.error(str(ex))

        return pods

    def get_events(self,namespace,podname):
        events = []
        try:
           url = "https://" + self.osHost + "/api/v1/namespaces/" + namespace + "/events"
           headers = {"Authorization" : "Bearer " + self.utils.get_token()}
           self.logger.info("GET EVENTS URL:" + url)
           retStatus = requests.get(url, headers=headers, verify=False)
           if isinstance(retStatus.content,bytes):
              self.logger.info("Ret Type is Bytes")
              strEvents = retStatus.content.decode("utf-8")
           else:
              strEvents = str(retStatus.content)
           nsEvents = json.loads(strEvents)
           for item in nsEvents["items"]:
               if podname == "None" or podname in str(item):
                  lastTime = item["lastTimestamp"]
                  utcTime = datetime.strptime(lastTime,self.dateTimeFormat)
                  localTime = self.utils.utc_to_local(utcTime,self.displayTimeFormat)
                  item["localizedTime"] = localTime
                  events.append(item)
        except Exception as ex:
           self.logger.error(str(ex))

        return events       

