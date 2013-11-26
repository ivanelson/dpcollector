'''
Created on 02/10/2013

@author: csmanioto
'''
from sys import platform as _platform
import time

from lib.collector.base.oscheck.MetaOS import MetaPosix
from lib.setup.Load import log, host_name, ntp_server
from lib.setup.Header import CONS_COLLECT_FOR
from lib.collector.base.WriteCache import WriteCache
from lib.common.powertools import get_unixtime_ntp_server, convert_now2unixtime, kbytes2bytes, fixfloat


if _platform == "darwin":
    from lib.collector.base.oscheck.MacOS import MacOS

    class MetaOS(MetaPosix, MacOS):
        pass

if _platform == "linux" or "linux2":
    from lib.collector.base.oscheck.Linux import Linux

    class MetaOS(MetaPosix, Linux):
        pass

if _platform == "freebsd":
    from lib.collector.base.oscheck.FreeBSD import FreeBSD

    class MetaOS(MetaPosix, FreeBSD):
        def __init__(self):
            pass

if _platform == "win32" or _platform == "winnt":
    from lib.collector.base.oscheck.Windows import Windows

    class MetaOS(Windows):
        def __init__(self):
            pass


class OS(MetaOS):
    '''
        Class OS content generic methots
    '''
    wcache = None

    def __init__(self, filename):
        self.wcache = WriteCache(host_name, filename)


    def write_key(self, key, value, ts=str(int(time.time()))):
        log.debug("get: %s" % key)
        self.wcache.toWrite(key, value, ts)

    def collect_mem_info(self, priority=2):
        ts = str(int(time.time()))
        if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
            meminfo = self.get_mem_info()
            self.write_key("os.mem_info.physical_total", fixfloat(kbytes2bytes(meminfo.memtotal)), ts)
            self.write_key("os.mem_info.physical_usage",
                           fixfloat(kbytes2bytes(long(meminfo.memtotal) - long(meminfo.memfree))), ts)
            self.write_key("os.mem_info.physical_free", fixfloat(kbytes2bytes(meminfo.memfree)), ts)
            self.write_key("os.mem_info.vm_cached", fixfloat(kbytes2bytes(meminfo.cached)), ts)
            self.write_key("os.mem_info.vm_buffers", fixfloat(kbytes2bytes(meminfo.buffers)), ts)
            self.write_key("os.mem_info.vm_swap_total", fixfloat(kbytes2bytes(meminfo.swaptotal)), ts)
            self.write_key("os.mem_info.vm_swap_free", fixfloat(kbytes2bytes(meminfo.swapfree)), ts)
            self.write_key("os.mem_info.vm_swap_usage",
                           fixfloat(kbytes2bytes(long(meminfo.swaptotal) - long(meminfo.swapfree))), ts)

    def collect_load_info(self, priority=1):
        ts = str(int(time.time()))

        if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
            av1, av2, av3 = self.get_os_loadvg()
            self.write_key("os.loadavg.one", round(av1, 2), ts)
            self.write_key("os.loadavg.five", round(av2, 2), ts)
            self.write_key("os.loadavg.fifteen", round(av3, 2), ts)
            self.write_key("os.cpu_usage", self.get_total_cpu_usage(), ts)


    def collect_hardware_info(self, priority=2):
        ts = str(int(time.time()))
        if priority == CONS_COLLECT_FOR["INVOKED"] or priority == CONS_COLLECT_FOR["BOOTH"]:
            self.write_key("hardware.name", self.get_os_hardware_name(), ts)
            self.write_key("hardware.cpuinfo", self.get_hardware_cpuinfo(), ts)

    def collect_os_info(self, priority=2):
        ts = str(int(time.time()))

        if priority == CONS_COLLECT_FOR["INVOKED"] or priority == CONS_COLLECT_FOR["BOOTH"]:
            self.write_key("os.info", self.get_os_distr(), ts)

    def collect_network_info(self, priority=1):
        ts = str(int(time.time()))
        if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
            self.write_key("network.bytes_rx",
                           self.get_network_stats_byiface(str(self.get_network_default_gateway_iface()))[0], ts)
            self.write_key("network.bytes_tx",
                           self.get_network_stats_byiface(str(self.get_network_default_gateway_iface()))[1], ts)

        if priority == CONS_COLLECT_FOR["INVOKED"] or priority == CONS_COLLECT_FOR["BOOTH"]:
            self.write_key("network.default_gateway", self.get_network_default_gateway(), ts)
            self.write_key("network.default_gateway_iface", self.get_network_default_gateway_iface(), ts)
            self.write_key("network.default_gateway_router", self.get_network_default_gateway_router(), ts)

    def collect_file_system_info(self, priority=1):
        ts = str(int(time.time()))
        rs = self.get_filesystem_info()
        if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
            for line in rs:
                part = line[0]
                alias = line[1]
                total = line[2]
                used = line[3]
                free = line[4]
                perc = line[5]
                self.write_key("os.file_system_partition_" + alias, part, ts)
                self.write_key("os.file_system_partition_alias_" + alias, alias, ts)
                self.write_key("os.file_system_total_" + alias, total, ts)
                self.write_key("os.file_system_used_" + alias, used, ts)
                self.write_key("os.file_system_free_" + alias, free, ts)
                self.write_key("os.file_system_perc_" + alias, perc, ts)

    def collect_ntp_date(self, priority=1):
        if ntp_server is not None:
            ts = str(int(time.time()))
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                try:
                    self.write_key("os.time_ntp_server", get_unixtime_ntp_server(), ts)
                    self.write_key("os.time_ntp_server_unixtime", convert_now2unixtime(get_unixtime_ntp_server()), ts)
                except:
                    pass


    def collect_all(self, priority):
        self.collect_ntp_date(priority)
        self.collect_mem_info(priority)
        self.collect_load_info(priority)
        self.collect_hardware_info(priority)
        self.collect_os_info(priority)
        self.collect_network_info(priority)
        self.collect_file_system_info(priority)
