'''
Created on 02/10/2013

@author: csmanioto
'''
from lib.setup.Load import CACHE_FILE_CONTINUOUS, CACHE_FILE_INVOKED
from lib.setup.Header import CONS_COLLECT_FOR
from lib.collector.base.oscheck.OS import OS


''' host_name is a global founded in lib.setup.Load
    This module impoterd by WriteCache
    host_name recevy Hostname value from zabbix_agentd.conf
    If null than host_name = Operational System Hostane
'''


class GetOS(object):
    filename = CACHE_FILE_INVOKED
    priority = None

    def __init__(self, priority):
        self.priority = priority
        if priority == CONS_COLLECT_FOR["INVOKED"]:
            self.filename = CACHE_FILE_INVOKED
        elif priority == CONS_COLLECT_FOR["CONTINUOUS"]:
            self.filename = CACHE_FILE_CONTINUOUS

    def collect(self):
        os_collect = OS(self.filename)
        os_collect.collect_all(self.priority)
    