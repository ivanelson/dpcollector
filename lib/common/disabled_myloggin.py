'''
Created on 13/09/2013

@author: csmanioto
http://victorlin.me/2012/08/good-logging-practice-in-python/
'''

import logging
import os


class LogManager():
    v_log = None
    log_level = None
    handler = None
    log_file_name = None

    def __init__(self, log_file_name, log_level, log_name):

        dirpath = os.path.dirname(log_file_name)
        if not os.path.exists(dirpath) or not os.path.isdir(dirpath):
            os.makedirs(dirpath)
        self.log_level = log_level
        self.log_file_name = log_file_name
        self.v_log = logging.getLogger(log_name)
        self.handler = logging.FileHandler(log_file_name)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        if log_level == 'INFO':
            self.v_log.setLevel(logging.INFO)
            self.handler.setLevel(logging.INFO)

        if log_level == 'WARN':
            self.v_log.setLevel(logging.WARN)
            self.handler.setLevel(logging.WARN)

        if log_level == 'DEBUG':
            self.v_log.setLevel(logging.DEBUG)
            self.handler.setLevel(logging.DEBUG)

        if log_level == 'ERROR':
            self.v_log.setLevel(logging.ERROR)
            self.handler.setLevel(logging.ERROR)

        if log_level == 'CRITCAL':
            self.v_log.setLevel(logging.CRITICAL)
            self.handler.setLevel(logging.CRITICAL)

        self.handler.setFormatter(formatter)
        self.v_log.addHandler(self.handler)


    def setLogName(self, name):
        self.v_log.name = name

    def logInfo(self, msg):
        if self.log_level <> "INFO":
            return None
            #self.v_log.setLevel(logging.INFO)
        #self.handler.setLevel(logging.INFO)
        self.v_log.info(msg)

    def logWarn(self, msg):
        if self.log_level <> "WARN":
            return None
        self.v_log.warning(msg)

    def logError(self, msg):
        if self.log_level <> "ERROR":
            return None
        self.v_log.error(msg)

    def logDegub(self, msg):
        if self.log_level <> "DEBUG":
            return None
            #self.v_log.setLevel(logging.DEBUG)
        #self.handler.setLevel(logging.DEBUG)
        self.v_log.debug(msg)

    def logCritical(self, msg):
        if self.log_level <> "CRITICAL":
            return None
        self.v_log.critical(msg)

    def logAllLevel(self, msg):
        if self.log_level == 'INFO':
            self.logInfo(msg)

        if self.log_level == 'WARN':
            self.logWarn(msg)

        if self.log_level == 'DEBUG':
            self.logDegub(msg)

        if self.log_level == 'ERROR':
            self.logError(msg)

        if self.log_level == 'CRITCAL':
            self.logCritical(msg)