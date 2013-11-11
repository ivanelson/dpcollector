import time

from lib.setup.Header import CONS_BIGIP_AVAIL, CONS_BIGIP_ENABLE, CONS_COLLECT_FOR
from lib.common.powertools import convert_bool_to_int, ip2long
from lib.collector.base.networkcheck.bigip.BigIPF5 import BigIPF5
from lib.collector.base.WriteCache import WriteCache
from lib.setup.Load import log, host_name, network_bigip_address, network_bigip_user_name, networl_bigip_user_password
from lib.collector.base.oscheck.OS import MetaOS


class BigIpCollector(object):
    '''
    classdocs
    '''

    wcache = None
    bigip = None
    enabled_in_poll = False
    exist_in_pool = False

    def __init__(self, filename):
        self.bigip = BigIPF5(network_bigip_address, network_bigip_user_name, networl_bigip_user_password)
        self.wcache = WriteCache(host_name, filename)

    def write_key(self, key, value, ts=str(int(time.time()))):
        log.debug("get: %s" % key)
        self.wcache.toWrite(key, value, ts)

    def check_host_bigip_pool(self):
        os_get = MetaOS()
        _local_ip_string = os_get.get_network_ip_byiface(os_get.get_network_default_gateway_iface())
        #_local_ip_string = '10.80.40.13'
        _local_ip_adrress_long = ip2long(_local_ip_string)
        log.debug("BigIP: Start query in pools... this very expensive...")
        for poolname in self.bigip.getAllPools():
            result_member = self.bigip.getAllMembersOfPool(poolname.strip())
            for row_host in result_member.keys():

                result_ip_address_long = ip2long(str(row_host))
                if _local_ip_adrress_long == result_ip_address_long:
                    self.exist_in_pool = True
                    log.debug("BigIP: This server(%s) has found in  %s" % (_local_ip_string, poolname))
                    avail = result_member.get(row_host).get('avail')
                    enabled = result_member.get(row_host).get('enabled')
                    cons_a = CONS_BIGIP_AVAIL.get(1)
                    cons_b = CONS_BIGIP_ENABLE.get(1)
                    if avail == cons_a and enabled == cons_b:
                        self.enabled_in_poll = True
                        log.debug(
                            "BigIP: This server(%s) has found in and Enabled :-) %s" % (_local_ip_string, poolname))
                        break
                    else: # Break internal loop for row_host
                        log.debug(
                            "BigIP: This server(%s) has found in %s but unavailable :-(" % (_local_ip_string, poolname))
                else:
                    continue
            if self.enabled_in_poll:
                break

    def collect_check_host_bigip_pool(self, priority=1):
        if priority == CONS_COLLECT_FOR["INVOKED"]:
            ts = str(int(time.time()))
            self.check_host_bigip_pool()
            self.write_key("net.bigip_f5.exist_in_pool", convert_bool_to_int(self.exist_in_pool), ts)
            self.write_key("net.bigip_f5.enabled_in_poll", convert_bool_to_int(self.enabled_in_poll), ts)                      