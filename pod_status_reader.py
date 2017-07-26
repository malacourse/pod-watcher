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
        self.filePath = "/var/lib/podstatus/"
        self.namespace = namespace
        self.logger = logging.getLogger(__name__)
        if "STATUSFILE" in os.environ:
           self.filePath = os.environ["STATUSFILE"] 
        self.osHost = "192.168.99.100:8443"
        self.osToken = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJ0ZXN0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InBvZHdhdGNoZXJzYS10b2tlbi03ZjNnMyIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJwb2R3YXRjaGVyc2EiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJiMDg5YzRhYS02YjFlLTExZTctYjdiOC0wODAwMjdlYTczYzciLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6dGVzdDpwb2R3YXRjaGVyc2EifQ.N_bYQs-Pg_1xpDg2M66xI4TM5ag2AOVYipgUBPptT6Z3qbR0q3RPyJVyTVnAvSFBhg2_kUT4WGGKi6qXzCwRBfXo_Yu_WCL4P-dTlZ0dd0OBNh-kbgPnSfsi0_j9lRBHtm-NH7BB037SiKLuzDY6A0q3QoUnUhzJDgLp9h3ci33CaXwLPUdFFHXhL0xj5yfahLyInCJL1jCK1vgylpynhDqEoeO4keOmA7OhEN6s1cdN6dDbTvr8leky1AKuIQYWJY_ieskULgusfvR99sRSKIBFklLQ1UXdLsmVFOXTdvc3HeO04B0kHsQminasJEFJ-0-v81DZkPq-Mt1O7lfMRA"
        self.logger = logging.getLogger(__name__)
        self.log_level = logging.INFO
        ## "2017-06-28T18:30:55Z"
        self.dateTimeFormat = "%Y-%m-%dT%H:%M:%SZ"
        self.displayTimeFormat = "%m/%d/%Y-%H:%M:%S"

        if "OPENSHIFT_HOST" in os.environ:
           self.osHost = os.environ["OPENSHIFT_HOST"]
        if "OPENSHIFT_NAMESPACE" in os.environ:
           self.osNs = os.environ["OPENSHIFT_NAMESPACE"]
        if "OPENSHIFT_TOKEN" in os.environ:
           self.osToken = os.environ["OPENSHIFT_TOKEN"]
        self.includeEvents = True
        if "PM_INCLUDE_EVENTS" in os.environ:
           self.includeEvents = os.environ["PM_INCLUDE_EVENTS"] == "True"
 

    def get_status_for_ns(self, namespace):
        # load from file:
        try:
            with open(self.filePath + namespace, 'rb') as f:
                data = pickle.load(f)
        except:
	        data = []
        self.logger.debug("Data:" + str(data))
        return data

    def get_status(self):
        # load from file:
        try:
            with open(self.filePath + self.namespace, 'rb') as f:
                data = pickle.load(f)
        except:
                data = []
        self.logger.debug("Data:" + str(data))
        return data

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
           self.logger.info("Header:" + str(headers))
           retStatus = requests.get(url, headers=headers, verify=False)
           nsPods = json.loads(str(retStatus.content))
           self.logger.info("PODS:" + str(nsPods))
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
           self.logger.info("EVENTS TYPE:" + str(type(retStatus.content)))
           if isinstance(retStatus.content,bytes):
              self.logger.info("Ret Type is Bytes")
              strEvents = retStatus.content.decode("utf-8")
           else:
              strEvents = str(retStatus.content)
           nsEvents = json.loads(strEvents)
           self.logger.info("EVEN NS:" + str(nsEvents))
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

