'''
Created on 01/10/2013

@author: csmanioto
'''
import os
import sys
import subprocess

from lib.setup.Load import zabbix_sender, zabbix_server_host, host_name, log
from lib.setup.Header import CONS_CLEAR_FILE_AFTER_TRAP
from lib.common.powertools import sizeof_fmt
from lib.setup.send.ZabbixSend import ZabbixSend

#fancy.logToScreen(enable=False)
#fancy.logToFile(log_file)
#fancy.setLogLevel(log_level)
#log = fancy.getLogger(__name__)



class CacheSender(object):
    '''
    classdocs
    '''
    filename = None

    def __init__(self, filename):
        '''
        Constructor
        '''
        self.filename = filename.strip()

    def clearfile(self):

        try:
            if CONS_CLEAR_FILE_AFTER_TRAP:
                os.remove(self.filename)
                log.debug("File " + self.filename + " removed after zabbix_send")
            else:
                log.debug("Delete file cache is disabled in source code: CONS_CLEAR_FILE_AFTER_TRAP = False")
        except IOError, ioe:
            log.debug("Error on remove file: " + str(ioe))


    def toZabbix(self):
        try:
            file_size = os.path.getsize(self.filename)
            cmd_send = "%s -z %s -s %s -T -i %s" % (
                str(zabbix_sender).strip(), str(zabbix_server_host).strip(), str(host_name).strip(),
                str(self.filename).strip())
            try:
                process = subprocess.Popen(cmd_send.strip(), shell=True, stdout=subprocess.PIPE)
                stdout = process.communicate()[0]
                process.wait()
                if sys.version_info >= (2, 7):
                    log.debug("Sending  %s  - %s " % (self.filename, sizeof_fmt(file_size)))
                    log.debug("Zabbix Server command: %s" % cmd_send)
                    log.debug("File %s -  sended by zabbix_sender %s: " % (str(self.filename), str(stdout)))
                else:
                    log.debug("Sending  %s" % (self.filename))
                    log.debug("Zabbix Server command: %s" % cmd_send)
                    log.debug("File %s -  sended by zabbix_sender %s: " % (str(self.filename), str(stdout)))
                return True
            except (IOError, Exception), e:
                log.debug("Error on zabbix_send - command " + cmd_send + " error: " + str(e))
            self.clearfile()
            return True
        except:
            log.debug("File %s is empty... I don't need send" % self.filename)
            return False
            pass


    def toZabbixNative(self):
        try:
            file_size = os.path.getsize(self.filename)
            z = ZabbixSend(server=str(zabbix_server_host).strip())
            try:
                data_file = open(self.filename, "r")
                for row in data_file:
                    z.add_data(row.strip())
                data_file.close()
                z.send(z.build_all())
                self.clearfile()
            except (IOError, Exception), e:
                log.debug("Error on send data to Zabbix (Native) - error: " + str(e))
            return True
        except:
            log.debug("File %s is empty... I don't need send" % self.filename)
            return False
            pass