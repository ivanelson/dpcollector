'''
Created on 17/09/2013

@author: csmanioto
'''
import fcntl
import struct
import subprocess
import os
import socket

from lib.common.powertools import convert_dict_to_object

#import psutil
from collections import namedtuple


class MacOS():
    '''
    classdocs
    '''

    disk_ntuple = namedtuple('partition', 'device mountpoint fstype')
    usage_ntuple = namedtuple('usage', 'total used free percent')


    def __init__(self):
        '''
        Constructor
        '''


    def get_network_default_gateway(self):
        cmd = "netstat -rn | grep 'default' | awk '{print $1}'"
        gateway = subprocess.check_output(cmd, shell=True).strip()
        if gateway == "default":
            return "0.0.0.0"
        else:
            return gateway

    def get_network_default_gateway_router(self):
        cmd = "netstat -rn | grep 'default' | awk '{print $2}'"
        router = subprocess.check_output(cmd, shell=True).strip()
        return router

    def get_network_default_gateway_iface(self):
        cmd = "netstat -rn | grep 'default' | awk '{print $6}'"
        iface = subprocess.check_output(cmd, shell=True).strip()
        return iface

    def get_network_hostname(self):
        host = os.popen('uname -n').read().strip()
        return host

    def get_network_mac_byiface(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = fcntl.ioctl(s.fileno(), 0x8927, struct.pack('256s', ifname[:15]))
        return ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]

    def get_network_ip_byiface(self, ifname):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        info = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))[20:24])
        return info


    def get_os_loadvg(self):
        return os.getloadavg()

    def get_os_hardware_name(self):
        command = 'system_profiler SPHardwareDataType |grep "Model Identi"|cut -d: -f2'
        valor = subprocess.check_output(command, shell=True).strip()
        return valor


    def get_os_currentPid(self):
        return os.getpid()

    def get_os_pid_byname(self, name):
        command = 'ps aux |grep ' + name
        pid = subprocess.check_output(command, shell=True).strip()
        return long(pid)

    def get_mem_info(self):
        status = {
            'memtotal': 0,
            'memtotal': 0,
            'memfree': 0,
            'cached': 0,
            'buffers': 0,
            'swaptotal': 0,
            'swapfree': 0
        }
        return convert_dict_to_object(status)


    def get_total_cpu_usage(self):
        cpuPct = 0
        return str('%.4f' % cpuPct)
            