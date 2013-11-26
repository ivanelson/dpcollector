'''
Created on 02/10/2013

@author: csmanioto
'''
import time

from lib.setup.Load import CACHE_FILE_CONTINUOUS, CACHE_FILE_INVOKED
from lib.setup.Load import log, host_name
from lib.setup.Header import CONS_COLLECT_FOR
from lib.collector.base.WriteCache import WriteCache


''' host_name is a global founded in lib.setup.Load
    This module impoterd by WriteCache
    host_name recevy Hostname value from zabbix_agentd.conf
    If null than host_name = Operational System Hostane
'''


class GetCollector(object):
    filename = CACHE_FILE_INVOKED
    priority = None
    wcache = None


    def __init__(self, priority):
        self.priority = priority
        if priority == CONS_COLLECT_FOR["INVOKED"]:
            self.filename = CACHE_FILE_INVOKED
        elif priority == CONS_COLLECT_FOR["CONTINUOUS"]:
            self.filename = CACHE_FILE_CONTINUOUS

    def write_key(self, key, value, ts=str(int(time.time()))):
        log.debug("get: %s" % key)
        self.wcache.toWrite(key, value, ts)

    def collect(self):
        if self.priority == CONS_COLLECT_FOR["CONTINUOUS"] or self.priority == CONS_COLLECT_FOR["BOOTH"]:
            ts = str(int(time.time()))
            wcache = WriteCache(host_name, self.filename)
            self.write_key("collect.ping", 1, ts)

