'''
Created on 17/09/2013

@author: csmanioto
'''
import fcntl
import struct
import platform
import re
import subprocess
import socket
import os
import sys
import time

#import psutil
from collections import namedtuple
from lib.common.powertools import convert_dict_to_object, kbytes2bytes
from lib.setup.Load import log
#from lib.LogManager import *
#from lib.Header import *

class Linux():
    '''
    classdocs
    '''

    disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
    usage_ntuple = namedtuple('usage', 'total used free percent')
    result_ntuple = namedtuple('partition', 'partition partition_alias total usage free percent')


    def __init__(self):
        '''
        Constructor
        '''


    def get_network_default_gateway(self):
        '''Read the default gateway directly from /proc.'''
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
            return str(socket.inet_ntoa(struct.pack("<L", int(fields[2], 16))))

    def get_network_default_gateway_router(self):
        '''Read the default gateway directly from /proc.'''
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
                hex_addr = int(fields[2], 16)
                struct.pack("<L", hex_addr)
        return socket.inet_ntoa(struct.pack("<L", hex_addr))

    def get_network_default_gateway_iface(self):
        '''Read the default gateway directly from /proc.'''
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                    continue
        return fields[0]


    def get_mem_info(self):
        status = {}
        with open("/proc/meminfo") as mem:
            for line in mem:
                key = line.strip().split()[0].split(':')[0]
                value = line.strip().split()[1]
                status[key.lower()] = kbytes2bytes(long(value))
        return convert_dict_to_object(status)


    def get_network_mac_byiface(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

    def get_network_ip_byiface(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
        return info

    def get_network_lanip(self):
        ip = socket.gethostbyname(socket.gethostname())
        if ip.startswith("127.") and os.name != "nt":
            interfaces = [
                "eth0",
                "eth1",
                "eth2",
                "wlan0",
                "wlan1",
                "wifi0",
                "ath0",
                "ath1",
                "ppp0",
            ]
            for ifname in interfaces:
                try:
                    ip = self.getIpByIface(ifname)
                    break
                except IOError, e:
                    self.log.error("Error on get Lan IP " + e)
                    self.log.debug("Error on get Lan IP " + e)
                    pass
        return ip

    def get_os_distr(self):
        distri = list(platform.linux_distribution())
        plataform = platform.machine()
        return " %s %s %s - %s" % (distri[0], distri[1], distri[2], plataform)

    def get_network_stats_byiface(self, ifname):

        for line in open('/proc/net/dev', 'r'):
            if ifname in line:
                data = line.split('%s:' % ifname)[1].split()
                rx_bytes_t1, tx_bytes_t1 = (data[0], data[8])
        '''
        # Calc per second.
        time.sleep(1)
        for line in open('/proc/net/dev', 'r'):
            if ifname in line:
                data = line.split('%s:' % ifname)[1].split()
                rx_bytes_t2, tx_bytes_t2 = (data[0], data[8])
                
        rx_bytes = long(rx_bytes_t2) - long(rx_bytes_t1)
        tx_bytes = long(tx_bytes_t2) - long(tx_bytes_t1)
        '''
        rx_bits = long(rx_bytes_t1) * 8
        tx_bits = long(tx_bytes_t1) * 8
        return str(rx_bits), str(tx_bits)


    def get_os_hardware_name(self):
        command = 'dmesg |grep "DMI:" |cut -d":" -f2'
        if sys.version_info >= (2, 7):
            valor = subprocess.check_output(command, shell=True).strip()
        else:
            valor = os.system(command)
        return valor

    def get_os_disk_partion(self, param_all=False):
        """Return param_all mountd partitions as a nameduple.
        If param_all == False return phyisical partitions only.
        """
        phydevs = []
        f = open("/proc/filesystems", "r")
        for line in f:
            if not line.startswith("nodev"):
                phydevs.append(line.strip())

        retlist = []
        f = open('/etc/mtab', "r")
        for line in f:
            if not param_all and line.startswith('none'):
                continue
            fields = line.split()
            device = fields[0]
            mountpoint = fields[1]
            fstype = fields[2]
            if not param_all and fstype not in phydevs:
                continue
            if device == 'none':
                device = ''
            ntuple = self.disk_ntuple(device, mountpoint, fstype)
            retlist.append(ntuple)
        return retlist

    def get_os_disk_usage(self, path):
        """Return disk usage associated with path."""
        st = os.statvfs(path)
        free = (st.f_bavail * st.f_frsize)
        total = (st.f_blocks * st.f_frsize)
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
        try:
            percent = (float(used) / total) * 100
        except ZeroDivisionError:
            percent = 0
            # NB: the percentage is -5% than what shown by df due to
        # reserved blocks that we are currently not considering:
        # http://goo.gl/sWGbH
        return self.usage_ntuple(total, used, free, round(percent, 1))

    def get_os_filesystem_size(self, mount_point):
        statvfs = os.statvfs(mount_point)
        statvfs.frsize * statvfs.f_blocks     # Size of filesystem in bytes
        statvfs.frsize * statvfs.f_bfree      # Actual number of free bytes
        statvfs.frsize * statvfs.f_bavail     # Number of free bytes that ordinary users
        return statvfs

    # usage(total=238787584, used=165148672, free=60899328, percent=69.2)
    def get_filesystem_info(self):
        my_list = self.get_os_disk_partion()
        rlist = []
        for disk in my_list:
            disk_part = disk[0]
            alias = disk[0].rsplit('/', 1)[1]
            stats_disk = self.get_os_disk_usage(str(disk[1]))
            total = stats_disk[0]
            used = stats_disk[1]
            free = stats_disk[2]
            percent = stats_disk[3]
            ntuple = self.result_ntuple(disk_part, alias, total, used, free, percent)
            rlist.append(ntuple)
        return rlist


    def get_os_pid_byname(self, name):
        command = 'ps aux |grep ' + name
        pid = os.popen(command).read()
        return long(pid)

    def get_hardware_cpuinfo(self):
        command = 'cat /proc/cpuinfo |grep "model name" |uniq'
        cpu_info = os.popen(command).read()

        command = "cat /proc/cpuinfo |grep processor|wc -l"
        processor = os.popen(command).read()

        for line in cpu_info.split("\n"):
            if "model name" in line:
                line = re.sub(".*model name.*:", "", line, 1)
        line += " with %s core(s) " % processor
        return line.replace("\n", "")


    ''' GET CPU % IN PYTON '''
    TIMEFORMAT = "%m/%d/%y %H:%M:%S"
    INTERVAL = 2

    def getTimeList(self):
        statFile = file("/proc/stat", "r")
        timeList = statFile.readline().split(" ")[2:6]
        statFile.close()
        for i in range(len(timeList)):
            timeList[i] = int(timeList[i])
        return timeList

    def deltaTime(self, interval):
        x = self.getTimeList()
        time.sleep(interval)
        y = self.getTimeList()
        for i in range(len(x)):
            y[i] -= x[i]
        return y

    def get_total_cpu_usage(self):
        dt = self.deltaTime(self.INTERVAL)
        cpuPct = 100 - (dt[len(dt) - 1] * 100.00 / sum(dt))
        return str('%.4f' % cpuPct)

    def get_folder_size(self, folder):
        ''' Return in K '''
        command = 'du -sc -b ' + folder
        try:
            du_info = os.popen(command).read()
            for line in du_info.split("\n"):
                if "total" in line:
                    line = line.strip().split()
                    return line[0]
        except Exception, e:
            log.debug("Error on get_folder_size: %s" % e)
            return 0

    def get_tcp_status(self, port, tcp_status):
        command = "netstat -nap |grep %s | grep '%s' |wc -l" % (port, tcp_status)
        try:
            netstat = os.popen(command).read()
            for line in netstat.split():
                pass
            return line[0]
        except Exception:
            return 0

    def get_pid_memory_info(self, pid=None, pid_file=None):
        status = {}
        try:
            if pid_file != None and pid == None:
                command = "cat %s" % pid_file
                result = os.popen(command).read()
                for line in result.split():
                    pass
                pid = line
        except Exception, e:
            log.debug("Error on get pid by pid_file: %s - %s" % (pid_file, e))
            pass

        #pid = 2200
        command = "cat /proc/%s/status" % pid
        result = os.popen(command).read()
        for line in result.split('\n'):
            if "VmPeak:" in line:
                status['vmpeak'] = kbytes2bytes(line.strip().split()[1])
            if "VmSize:" in line:
                status['vmsize'] = kbytes2bytes(line.strip().split()[1])
            if "VmLck" in line:
                status['vmlck'] = kbytes2bytes(line.strip().split()[1])
            if "VmHWM:" in line:
                status['vmhwm'] = kbytes2bytes(line.strip().split()[1])
            if "VmRSS:" in line:
                status['vmrss'] = kbytes2bytes(line.strip().split()[1])
            if "VmData:" in line:
                status['vmdata:'] = kbytes2bytes(line.strip().split()[1])
            if "VmStk:" in line:
                status['vmstk'] = kbytes2bytes(line.strip().split()[1])
            if "VmExe:" in line:
                status['vmexe'] = kbytes2bytes(line.strip().split()[1])
            if "VmLib:" in line:
                status['vmlib'] = kbytes2bytes(line.strip().split()[1])
            if "VmPTE:" in line:
                status['vmpte'] = kbytes2bytes(line.strip().split()[1])
            if "VmSwap:" in line:
                status['vmswap'] = kbytes2bytes(line.strip().split()[1])
        return status
                
            
            