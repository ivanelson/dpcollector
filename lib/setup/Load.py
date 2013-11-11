import os
import socket
import logging
import sys

from lib.setup.Header import CONS_CONFIG_FILE, DEFAULT_LOGGING_FORMAT, CONS_NTP_GRACE_TIME, CONS_PRODUCT_NAME, CONS_INVOKED_SLEEP_TIME, CONS_CONTINUOUS_SlEEP_TIME
from lib.setup.Header import CONS_DOMAIN
from lib.setup.Configuration_File import Configuration_File
from lib.common.powertools import parse_config_file, get_loggin_level


sys.setrecursionlimit(199999)
'''
Making/Read config
'''
dirpath = os.path.dirname(CONS_CONFIG_FILE)
if dirpath != "" or None:
    if not os.path.exists(dirpath) or not os.path.isdir(dirpath):
        os.makedirs(dirpath)
from_config_file = Configuration_File(CONS_CONFIG_FILE, 'wr') # Make if not exist and read or read if exist

#System Section
have_section = from_config_file.have
pid_file_path = from_config_file.system_pid_file_path
ntp_server = from_config_file.system_ntp_server
ntp_grace_time = int(from_config_file.system_ntp_grace_seconds.replace("", str(CONS_NTP_GRACE_TIME)))
host_name = socket.gethostname()
continuos_sleep_time = from_config_file.system_continuos_sleep_time
invoked_sleep_time = from_config_file.system_invoked_sleep_time

host_alias = from_config_file.system_host_name
if host_alias != None:
    host_name = host_alias

if continuos_sleep_time == None:
    continuos_sleep_time = CONS_CONTINUOUS_SlEEP_TIME
if invoked_sleep_time == None:
    invoked_sleep_time = CONS_INVOKED_SLEEP_TIME

CACHE_FILE_INVOKED = '/tmp/collector_' + host_name + '_' + CONS_DOMAIN + "invoked.cache"
CACHE_FILE_CONTINUOUS = '/tmp/collector_' + host_name + '_' + CONS_DOMAIN + "continuous.cache"



# Zabbix Agentd Setup
if 'zabbix' in have_section:
    zabbix_sender = from_config_file.zabbix_sender
    zabbix_cfg = from_config_file.zabbix_cfg_file
    zabbix_server_host = None
    zabbix_server_port = None
    # If exist zabbix_agentd.conf
    if zabbix_cfg != None:
        zabbix_agentd_cfg = parse_config_file(zabbix_cfg)
        try:
            host_name = str(zabbix_agentd_cfg.Hostname).strip()
        except:
            pass
        try:
            zabbix_server_host = str(zabbix_agentd_cfg.Server).strip()
        except:
            zabbix_server_host = None
        try:
            zabbix_server_port = zabbix_agentd_cfg.ServerPort
        except:
            zabbix_server_port = "10051"

    if zabbix_server_host == None:
        zabbix_server_host = from_config_file.zabbix_server

    if zabbix_server_port == None:
        zabbix_server_port = "10051"
# End of Zabbix setting.


''' Database get from config '''
if 'mysql' in have_section:
    db_mysql_user = from_config_file.db_mysql_user
    db_mysql_password = from_config_file.db_mysql_password
    db_mysql_hostname = from_config_file.db_mysql_hostname
    db_mysql_socket = from_config_file.db_mysql_socket
    db_mysql_modules = from_config_file.db_mysql_modules.split(',')
    if db_mysql_socket == None or db_mysql_socket == '':
        db_mysql_socket = False

if 'postgresql' in have_section:
    db_postgresql_user = from_config_file.db_postgresql_user
    db_postgresql_password = from_config_file.db_postgresql_password
    db_postgresql_hostname = from_config_file.db_postgresql_hostname
    db_postgresql_socket = from_config_file.db_postgresql_socket
    db_postgresql_modules = from_config_file.db_postgresql_modules
    if db_postgresql_socket == None or db_postgresql_socket == '':
        db_postgresql_socket = False

if 'sqlserver' in have_section:
    db_sqlserver_password = from_config_file.db_sqlserver_password
    db_sqlserver_hostname = from_config_file.db_sqlserver_hostname
    db_sqlserver_modules = from_config_file.db_sqlserver_modules
    db_sqlserver_port = from_config_file.db_sqlserver_port

if 'network' in have_section:
    if 'bigip' in have_section:
        network_bigip_check = from_config_file.network_bigip_enabled
        network_bigip_address = from_config_file.network_bigip_address
        network_bigip_user_name = from_config_file.network_bigip_user_name
        networl_bigip_user_password = from_config_file.networl_bigip_user_password

''' Logging Setup '''
log_file = from_config_file.system_log_filename
log_level = from_config_file.system_log_level
log = logging.getLogger(CONS_PRODUCT_NAME)


def set_log():
    log.setLevel(get_loggin_level(log_level))
    fh = logging.FileHandler(log_file)
    fh.setLevel(get_loggin_level(log_level))
    fhFormatter = logging.Formatter(DEFAULT_LOGGING_FORMAT)
    fh.setFormatter(fhFormatter)
    log.addHandler(fh)
    return fh


    