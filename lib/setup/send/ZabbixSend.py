__author__ = 'csmanioto'

import socket
import struct
import json
import time
import re

from lib.setup.Load import log


ZABBIX_SERVER = "127.0.0.1"
ZABBIX_PORT = 10051


class ZabbixSend:
    def __init__(self, server=ZABBIX_SERVER, port=ZABBIX_PORT):
        self.zserver = server
        self.zport = port
        self.list = []
        self.inittime = int(round(time.time()))
        self.header = '''ZBXD\1%s%s'''
        # localhost mysql.show_status.created_tmp_tables 1383845532 1
        self.datastruct = ''' { "host":"%s", "key":"%s", "clock":%s, "value":"%s" }'''

    def add_data(self, host, key, value, evt_time=None):
        if evt_time is None:
            evt_time = self.inittime
        self.list.append((host, key, evt_time, value))

    def print_vals(self):
        for (h, k, v, t) in self.list:
            print "Host: %s, Key: %s, Value: %s, Event: %s" % (h, k, v, t)

    def build_all(self):
        tmpdata = "{\"request\":\"sender data\",\"data\":["
        count = 0
        for (h, k, v, t) in self.list:
            tmpdata = tmpdata + self.datastruct % (h, k, v, t)
            count += 1
            if count < len(self.list):
                tmpdata = tmpdata + ","
        tmpdata = tmpdata + "], \"clock\":%s}" % self.inittime
        return (tmpdata)

    def build_single(self, dataset):
        tmpdata = "{\"request\":\"sender data\",\"data\":["
        (h, k, v, t) = dataset
        tmpdata = tmpdata + self.datastruct % (h, k, v, t)
        tmpdata = tmpdata + "], \"clock\":%s}" % self.inittime
        return (tmpdata)

    def send(self, mydata):
        socket.setdefaulttimeout(5)
        data_length = len(mydata)
        data_header = struct.pack('i', data_length) + '\0\0\0\0'
        data_to_send = self.header % (data_header, mydata)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.zserver, self.zport))
            sock.send(data_to_send)
        except Exception as err:
            log.debug("Zabbix Send: Error talking to server: %s\n" % err)
            return (255, err)
        try:
            response_header = sock.recv(5)
            if not response_header == 'ZBXD\1':
                log.debug("Zabbix Send: Invalid response from server. Malformed data?\n---\n%s\n---\n" % mydata)
        except Exception as err:
            return (254, err)
        response_data_header = sock.recv(8)
        response_data_header = response_data_header[:4]
        response_len = struct.unpack('i', response_data_header)[0]
        response_raw = sock.recv(response_len)
        sock.close()
        response = json.loads(response_raw)
        match = re.match("^.*Failed\s(\d+)\s.*$", str(response))
        if match is None:
            log.debug("Unable to parse server response - " + \
                      "\n%s\n" % response)
        else:
            fails = int(match.group(1))
            if fails > 0:
                log.debug("Zabbix Send: Failures reported by zabbix when sending:" + \
                          "\n%s\n" % mydata)
                return (1, response)
        return (0, response)

    def bulk_send(self):
        data = self.build_all()
        result = self.send(data)
        return result

    def iter_send(self):
        retarray = []
        for i in self.list:
            (retcode, retstring) = self.send(self.build_single(i))
            retarray.append((retcode, i))
        return retarray
