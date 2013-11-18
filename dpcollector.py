#!/usr/bin/python
'''
Created on 01/10/2013

@author: csmanioto
'''

#third party libs
from threading import Thread

from daemon import runner



#from lib.setup.Load import *
from lib.collector.Collector import Collector
from lib.setup.Header import CONS_PRODUCT_NAME
from lib.setup.Load import pid_file_path, set_log, log, invoked_sleep_time, continuos_sleep_time
import time, sys


#fancy.logToFile(log_file)
#fancy.setLogLevel(log_level)
#log = fancy.getLogger("main")

handler = set_log()

''' My implementation of reload into runner.DaemonRunner '''


class my_DaemonRunner(runner.DaemonRunner):
    # My Custom
    def _reload(self):
        self.app.reload()

    runner.DaemonRunner.action_funcs = {
        u'start': runner.DaemonRunner._start,
        u'stop': runner.DaemonRunner._stop,
        u'restart': runner.DaemonRunner._restart,
        u'reload': _reload,
    }


# Core Base


def call_invoked():
    while True:
        # if reload
        log.debug("Thread Invoked Started")
        collector = Collector()
        collector.Invoked()
        time.sleep(long(invoked_sleep_time)) # Load module - dpcollector.conf or CONSTANT


# Continuous Base


def call_continuous():
    while True:
        log.debug("Thread Continuous Started")
        collector = Collector()
        collector.Continuous()
        time.sleep(long(continuos_sleep_time)) # Load module - dpcollector.conf or CONSTANT


# App's is name called by runner


class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = '/dev/tty'
        self.stderr_path = '/dev/tty'
        self.pidfile_path = pid_file_path
        self.pidfile_timeout = 5

    def reload(self):
        log.debug("Reload Signal - Thread by external call starting")
        call_invoked()

    def run(self):
        log.info("-------------------------------------------")
        log.info("%s successfully initialised   " % CONS_PRODUCT_NAME)
        log.info("-------------------------------------------")

        th_invoked = Thread(target=call_invoked, args=())
        th_collector = Thread(target=call_continuous, args=())
        #th_collector.daemon = True
        #th_collector.daemon = True
        print "Starting Invoked Thread"
        th_invoked.start()
        print "Starting Continuous Thread"
        th_collector.start()

        #th_collector.join()
        #th_invoked.join()    


DEV = True

if not DEV:
    try:
        if sys.argv[1] == None or sys.argv[1] == "start" or sys.argv[1] == "stop" or sys.argv[1] == "restart" or sys.argv[1] == "reload":
            pass
        else:
            print "Parameter '%s' is  not valid: Valid only [start|stop|restart|reload]" % sys.argv[1]
            sys.exit(1)
    except:
        print "%s: [start|stop|restart|reload]" % CONS_PRODUCT_NAME
        sys.exit(1)

    if sys.argv[1] == "stop":
        log.info("-----------------------------------")
        log.info("%s successfully shutdown      " % CONS_PRODUCT_NAME)
        log.info("-----------------------------------")

app = App()

if not DEV:
    daemon_runner = my_DaemonRunner(app)
    daemon_runner.daemon_context.files_preserve = [handler.stream]
    daemon_runner.do_action()
else:
    app.run()
        
