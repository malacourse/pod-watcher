#!/usr/bin/python2.7
import logging
import pickle
import os

class PodStatusReader():


    def __init__(self):
        self.filePath = "/var/lib/podstatus/pod_status.txt"
        self.logger = logging.getLogger(__name__)
        if "STATUSFILE" in os.environ:
           self.filePath = os.environ["STATUSFILE"]

    def get_status(self):
        # load from file:
        with open(self.filePath, 'r') as f:
            try:
                data = pickle.load(f)
            except ValueError:
                data = {}
        return data

