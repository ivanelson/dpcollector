'''
Created on 02/10/2013

@author: csmanioto
'''

from lib.setup.Load import have_section, network_bigip_check, CACHE_FILE_INVOKED, CACHE_FILE_CONTINUOUS
from lib.common.powertools import convert2bool
from lib.setup.Header import CONS_COLLECT_FOR


class GetNet(object):
    filename = None
    priority = None

    def __del__(self):
        pass

    def __init__(self, priority):
        self.priority = priority
        if priority == CONS_COLLECT_FOR["INVOKED"]:
            self.filename = CACHE_FILE_INVOKED
        elif priority == CONS_COLLECT_FOR["CONTINUOUS"]:
            self.filename = CACHE_FILE_CONTINUOUS

    def collect(self):
        if 'network' in have_section:
            pass
            if 'bigip' in have_section:
                if convert2bool(network_bigip_check):
                    from lib.collector.base.networkcheck.BIGIP import BigIpCollector

                    bigip = BigIpCollector(self.filename)
                    bigip.collect_check_host_bigip_pool(self.priority)
            if 'switch_cisco' in have_section:
            #from lib.collector.base.networkcheck.cisco_switch import CiscoCollector
                pass
                     
