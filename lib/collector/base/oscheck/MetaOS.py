# https://code.google.com/p/psutil/
# Replace by psutil
import os
import socket
import psutil


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

    def get_pid_amount(self):
        return len(psutil.get_pid_list())

    def get_os_pid_byname(self, name):
        command = 'ps aux |grep ' + name
        pid = os.popen(command).read()
        return long(pid)

    def get_total_cpu_usage(self):
        return psutil.cpu_times_percent()[0]


