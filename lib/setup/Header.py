'''
Created on 01/10/2013

@author: csmanioto@gmail.com
'''

# Note:  more names are added to __all__ later.
__all__ = ["CONS_ERROR", "CONS_BIGIP_STATUS", "CONS_DOMAIN", "CONS_CONFIG_FILE", "CONS_CACHE_FILE_INVOKED",
           "DEFAULT_LOGGING_FORMAT"]

CONS_DOMAIN = "datapower.com.br" + "."
CONS_PRODUCT_NAME = "Data Power Collector"
CONS_COLLECT_FOR = {"INVOKED": 1, "CONTINUOUS": 2, "BOOTH": 3}
CONS_RAM_SERVER = 137438953472 # 128GB RAM - Used when collector not get physical ram ou error
CONS_ERROR = {"DBG": 4, "INFO": 3, "WARN": 2, "ERR": 1}
CONS_BIGIP_ENABLE = {1: "ENABLED_STATUS_ENABLED", 0: "ENABLED_STATUS_DISABLED"}
CONS_BIGIP_AVAIL = {0: "AVAILABILITY_STATUS_RED", 1: "AVAILABILITY_STATUS_GREEN"}
CONS_CONFIG_FILE = 'dpcollector.conf'
#DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(levelname)- %(name)s - %(threadname)s -  %(message)s'
#DEFAULT_LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEFAULT_LOGGING_FORMAT = '%(asctime)s - pid: %(process)s - %(name)s - %(levelname)s - %(message)s'
MYSQL_CONNECTION_TIMEOUT = 90
PGSQL_CONNECTION_TIMEOUT = 90
CONS_NTP_SERVER = 'pool.ntp.org'
CONS_NTP_GRACE_TIME = 03
CONS_CLEAR_FILE_AFTER_TRAP = True
CONS_INVOKED_SLEEP_TIME = 1800 # 30 minutes 
CONS_CONTINUOUS_SlEEP_TIME = 3 # 3 seconds