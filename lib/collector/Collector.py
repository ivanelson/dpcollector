'''
Created on 17/09/2013

@author: csmanioto
'''

from lib.collector.get_os import GetOS
from lib.collector.get_db import GetDB
from lib.collector.get_net import GetNet
from lib.collector.base.CacheSender import CacheSender
from lib.setup.Load import log, have_section, CACHE_FILE_CONTINUOUS, CACHE_FILE_INVOKED
from lib.setup.Header import CONS_COLLECT_FOR
#fancy.logToFile(log_file)
#fancy.setLogLevel(log_level)
#log = fancy.getLogger(__name__)
#from lib.collector.oscheck.OS import *



class Collector(object):
    log = None

    def __init__(self):
        pass

    def sendData(self, filename):
        send = CacheSender(filename)
        try:
            if 'zabbix' in have_section:
                send.toZabbixNative()
            if 'nagios' in have_section:
                pass
            if 'json' in have_section:
                pass
        except:
            pass


    def Invoked(self):
        log.debug("Collector -  OS - Base - Invoked Thread")
        get_os = GetOS(CONS_COLLECT_FOR["INVOKED"])
        get_os.collect()

        log.debug("Collector -  DB - Base - Invoked Thread")
        get_db = GetDB(CONS_COLLECT_FOR["INVOKED"])
        get_db.collect()

        log.debug("Collector -  Net - Base - Invoked Thread")
        get_net = GetNet(CONS_COLLECT_FOR["INVOKED"])
        get_net.collect()

        self.sendData(CACHE_FILE_INVOKED)

    def Continuous(self):
        log.debug("Collector -  DB - Base - Continuos Thread")
        get_db = GetDB(CONS_COLLECT_FOR["CONTINUOUS"])
        get_db.collect()

        log.debug("Collector -  OS - Base - Continuos Thread")
        get_os = GetOS(CONS_COLLECT_FOR["CONTINUOUS"])
        get_os.collect()

        log.debug("Collector -  Net - Base - Continuos Thread")
        get_net = GetNet(CONS_COLLECT_FOR["CONTINUOUS"])
        get_net.collect()

        #Send data
        self.sendData(CACHE_FILE_CONTINUOUS)
        pass
        #from lib.collector.OScollector_CRITICAL import *
        #from lib.collector.DBcollector_CRITICAL import *
        