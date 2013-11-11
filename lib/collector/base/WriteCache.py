'''
Created on 01/10/2013

@author: csmanioto
'''

import datetime
import sys
import time
from collections import deque

from lib.setup.Header import CONS_DOMAIN
from lib.setup.Load import log


#fancy.logToScreen(enable=False)
#fancy.logToFile(log_file)
#fancy.setLogLevel(log_level)

class WriteCache(object):
    '''
    classdocs
    '''
    host_name = None
    max_buffer_size = None
    filename = None
    current_time = datetime.datetime.now()

    ts = int(time.time())
    #log.setLogName("pyabbix")

    queue = deque()
    buffered = True
    send = None

    def __init__(self, host_name, filename, max_buffer_size=None, Buffered=False):
        '''
        Constructor
        '''
        self.filename = filename
        self.buffered = Buffered
        self.max_buffer_size = max_buffer_size
        self.host_name = host_name


    def toDisk(self, my_object):
        try:
            log.debug("==== Write data to disk =====")
            if type(my_object) == type(str()) or type(unicode()):
                log.debug("Object type str - Continue with simple mode")
                with open(self.filename, 'a') as f:
                    f.write(my_object + "\n")
                    log.debug("Write: flush to disk...You write %s (%d bytes)." % (self.filename, len(my_object)))
            else:
                while my_object:
                    with open(self.filename, 'a') as f:
                        f.write(my_object.popleft())
                        log.debug("Write: flush to disk %s (%d bytes)." % (self.filename, len(my_object)))
        except (OSError, IOError), e:
            log.debug("Error: Write data to disk: " + str(e))

    def toBuffer(self, line):
        log.debug("Sending data do Buffer")
        size = sys.getsizeof(self.queue) - 624 # 624 is a deque size when empty
        if self.max_buffer_size:
            if size > long(self.max_buffer_size):
                log.debug("Pyabbix flush to disk...buffer full: " + str(size))
                self.toDisk(self.queue)
        else:
            self.queue.append(line)


    def toWrite(self, key, value, timestamp=None):
        if timestamp == None:
            timestamp = str(self.ts)
        try:
            key = CONS_DOMAIN + key
        except:
            pass
        line = "%s %s %s %s" % (self.host_name, key, timestamp, value)
        log.debug("Write line %s" % line)
        if self.buffered:
            self.toBuffer(line)
        else:
            self.toDisk(line)
                       
        