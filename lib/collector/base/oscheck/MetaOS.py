# https://code.google.com/p/psutil/
# Replace by psutil
import os
import socket
import psutil

psutil.loa


class MetaPosix():
    def __init__(self):
        pass

    def get_network_hostname(self):
        return socket.gethostname()

    def get_os_loadvg(self):
        os.getloadavg()
        return os.getloadavg()

    def get_os_currentPid(self):
        return os.getpid()
 
