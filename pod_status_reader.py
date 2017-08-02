#!/usr/bin/python2.7
import logging
import pickle
import os
import json
import requests
from datetime import datetime, timedelta
from pytz import utc, timezone

class PodStatusReader():

    def __init__(self,namespace="None"):
        self.filePath = "/var/tmp/"
        self.secretPath = "/etc/secret"
        self.namespace = namespace
        self.logger = logging.getLogger(__name__)
        if "PODMONITOR_FILEPATH" in os.environ:
           self.filePath = os.environ["PODMONITOR_FILEPATH"] 
        self.osHost = ""
        self.osToken = ""
        self.logger = logging.getLogger(__name__)
        self.log_level = logging.INFO
        ## "2017-06-28T18:30:55Z"
        self.dateTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
        self.displayTimeFormat = "%m/%d/%Y-%H:%M:%S"

        token = self.load_token_from_secret()
        if token != "":
            self.osToken = token

        if "OPENSHIFT_HOST" in os.environ:
           self.osHost = os.environ["OPENSHIFT_HOST"]
        if "OPENSHIFT_NAMESPACE" in os.environ:
           self.osNs = os.environ["OPENSHIFT_NAMESPACE"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]
        self.includeEvents = True
        if "PODMONITOR_INCLUDE_EVENTS" in os.environ:
           self.includeEvents = os.environ["PODMONITOR_INCLUDE_EVENTS"].lower() == "true"
 
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

    def get_status(self):
        # load from file:
        try:
            with open(self.filePath + self.namespace, 'rb') as f:
                data = pickle.load(f)
                data = self.format_restart_times(data)
        except:
                self.logger.error("%s", traceback.format_exc())
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
                localTime = self.utc_to_local(utcTime)
                formatedRestarts.append(localTime)
          pod["restartsLocal"] = formatedRestarts
       return pods

    def save_status(self, ps, namespace):
        # save to file:
        with open(self.filePath + namespace, 'wb') as f:
            pickle.dump(ps, f)
            f.close()

    def get_alerts(self,namespaces):
        retStatus = []
        for namespace in namespaces:
           status = self.get_status_for_ns(namespace)
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
               self.save_status(status,namespace)
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

    local_tz = timezone('America/New_York')
    def utc_to_local(self, utc_dt):
        self.logger.debug("UTC TIME:" + str(utc_dt))
        local_dt = utc_dt.replace(tzinfo=utc).astimezone(self.local_tz)
        self.logger.debug("UTC NEW TIME:" + str(local_dt))
        return self.local_tz.normalize(local_dt).strftime(self.displayTimeFormat)


    def get_events(self,namespace,podname):
        events = []
        try:
           url = "https://" + self.osHost + "/api/v1/namespaces/" + namespace + "/events"
           headers = {"Authorization" : "Bearer " + self.osToken}
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
                  localTime = self.utc_to_local(utcTime)
                  item["localizedTime"] = localTime
                  events.append(item)
        except Exception as ex:
           self.logger.error(str(ex))

        return events       

