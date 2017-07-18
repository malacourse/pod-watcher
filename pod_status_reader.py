#!/usr/bin/python2.7
import logging
import pickle
import os
import json

class PodStatusReader():

    def __init__(self):
        self.filePath = "/var/lib/podstatus/pod_status.txt"
        self.logger = logging.getLogger(__name__)
        if "STATUSFILE" in os.environ:
           self.filePath = os.environ["STATUSFILE"]

    def get_status(self):
        # load from file:
        try:
            with open(self.filePath, 'rb') as f:
                data = pickle.load(f)
        except:
	        data = []
        self.logger.debug("Data:" + str(data))
        return data

    def save_status(self, ps):
        # save to file:
        with open(self.filePath, 'wb') as f:
            pickle.dump(ps, f)
            f.close()

    def get_alerts(self):
        status = self.get_status()
        retStatus = []
        for ps in status:
           if ps["alertStatus"] == "Warn":
              retStatus.append(dict(ps))
              ps["alertStatus"] = "Sent"
              ps["restarts"] = []
              ps["currentRestarts"] = 0

        if len(retStatus) > 0:
            self.logger.info("Reported alerts")
            self.save_status(status)
        return json.dumps(retStatus)             
       

