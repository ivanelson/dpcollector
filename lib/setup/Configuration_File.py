'''
Created on 13/09/2013

@author: csmanioto
http://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/ConfigParser/index.html
'''

import os

import ConfigParser
from lib.setup.Header import CONS_NTP_SERVER, CONS_INVOKED_SLEEP_TIME, CONS_CONTINUOUS_SlEEP_TIME


class Configuration_File:
    file_name = None
    file_permission = None

    system_log_level = None
    system_log_filename = None
    system_log_format = None
    system_host_name = None
    system_pid_file_path = None
    system_ntp_server = None
    system_ntp_grace_seconds = None
    system_continuos_sleep_time = None
    system_invoked_sleep_time = None

    db_mysql_hostname = None
    db_mysql_socket = None
    db_mysql_user = None
    db_mysql_password = None
    db_mysql_modules = None

    db_postgresql_hostname = None
    db_postgresql_socket = None
    db_postgresql_user = None
    db_postgresql_password = None
    db_postgresql_modules = None

    db_sqlserver_hostname = None
    db_sqlserver_user = None
    db_sqlserver_password = None
    db_sqlserver_modules = None
    db_sqlserver_port = None

    zabbix_sender = None
    zabbix_cfg_file = None
    zabbix_server = None

    network_bigip_enabled = False
    network_bigip_address = None
    network_bigip_user_name = None
    networl_bigip_user_password = None

    have = []

    def __init__(self, file_name, file_permission):
        self.file_name = file_name
        self.file_permission = file_permission
        self.makeFile()
        self.readFile()

    def makeFile(self):
        if os.path.isfile(self.file_name) == False:
            config = ConfigParser.RawConfigParser()

            ### Master Session
            config.add_section('system')
            config.set('system', 'log_level', 'INFO ; INFO, WARN, ERROR, DEBUG, CRITICAL')
            config.set('system', 'log_folder', 'dpcollector.log')
            config.set('system', 'pid_file', '/tmp/dpcollector.pid')
            config.set('system', 'thread_invoked_time', CONS_INVOKED_SLEEP_TIME)
            config.set('system', 'thread_continuous_time', CONS_CONTINUOUS_SlEEP_TIME)
            config.set('system', 'ntp_server', CONS_NTP_SERVER)
            config.set('system', 'ntp_grace_time', '05')
            config.set('system', 'hostname_alias', 'instance2')

            # Trap to Zabbix
            config.add_section('zabbix')
            config.set('zabbix', 'config', '/etc/zabbix/zabbix_agentd.conf')
            config.set('zabbix', 'zabbix_sender_path', '/usr/bin/zabbix_sender')
            config.set('zabbix', 'zabbix_server', 'dhc-zabbix01.servers')

            # MySQL Mon
            config.add_section('mysql')
            config.set('mysql', 'user', 'root')
            config.set('mysql', 'password', 'passWord')
            config.set('mysql', 'hostname', '127.0.0.1')
            config.set('mysql', 'socket', '/mysql/mysql.sock')
            config.set('mysql', 'port', '3306')
            config.set('mysql', 'modules', 'common, slave, master')

            # PostgreSQL Mon
            config.add_section('postgresql')
            config.set('postgresql', 'user', 'postgres')
            config.set('postgresql', 'password', 'passWord')
            config.set('postgresql', 'hostname', '127.0.0.1')
            config.set('postgresql', 'socket', '/tmp/psql.sock')
            config.set('postgresql', 'port', '5432')
            config.set('postgresql', 'modules', 'common ; slony-slave, slony-master, pg-slave, pg-master')

            # SQL Server Mon
            config.add_section('sqlserver')
            config.set('sqlserver', 'user', 'sa')
            config.set('sqlserver', 'password', 'passWord')
            config.set('sqlserver', 'hostname', '127.0.0.1')
            config.set('sqlserver', 'port', '1433')
            config.set('sqlserver', 'modules', 'common')

            # NetWork Mon
            config.add_section('network')
            config.set('network', 'bigip_enable', 'False')
            config.set('network', 'bigip_address', '10.10.10.10')
            config.set('network', 'bigip_user_name', 'admin')
            config.set('network', 'bigip_user_password', 'admin')
            with open(self.file_name, self.file_permission) as configfile:
                config.write(configfile)

                # Apache Mon


                # Tomcat Mon

                # Solr Mon

                # Mongo Mon


    def readFile(self):
        # makeFile(self)
        config = ConfigParser.ConfigParser()

        try:
            config.read(self.file_name)

            if config.has_section('mysql'):
                self.have.append('mysql')
                self.db_mysql_user = config.get('mysql', 'user')
                self.db_mysql_password = config.get('mysql', 'password')
                self.db_mysql_hostname = config.get('mysql', 'hostname')
                self.db_mysql_socket = config.get('mysql', 'socket')
                self.db_mysql_port = config.get('mysql', 'port')
                self.db_mysql_modules = config.get('mysql', 'modules')

            if config.has_section('postgresql'):
                self.have.append('postgresql')
                self.db_postgresql_user = config.get('postgresql', 'user')
                self.db_postgresql_password = config.get('postgresql', 'password')
                self.db_postgresql_hostname = config.get('postgresql', 'hostname')
                self.db_postgresql_port = config.get('postgresql', 'port')
                self.db_postgresql_socket = config.get('postgresql', 'socket')
                self.db_postgresql_modules = config.get('postgresql', 'modules')

            if config.has_section('sqlserver'):
                self.have.append('sqlserver')
                self.db_postgresql_user = config.get('sqlserver', 'user')
                self.db_postgresql_password = config.get('sqlserver', 'password')
                self.db_postgresql_hostname = config.get('sqlserver', 'hostname')
                self.db_postgresql_port = config.get('sqlserver', 'port')
                self.db_postgresql_modules = config.get('sqlserver', 'modules')

            if config.has_section('system'):
                self.system_log_level = config.get('system', 'log_level').upper()
                self.system_log_filename = config.get('system', 'log_folder')

                if config.has_option('system', 'hostname_alias'):
                    self.system_host_name = config.get('system', 'hostname_alias')
                else:
                    self.system_pid_file_path = 'pyabbix.pid'

                if config.has_option('system', 'pid_file'):
                    self.system_pid_file_path = config.get('system', 'pid_file')
                else:
                    self.system_pid_file_path = 'pyabbix.pid'

                if config.has_option('system', 'ntp_server'):
                    self.system_ntp_server = config.get('system', 'ntp_server')
                    self.system_ntp_grace_seconds = config.get('system', 'ntp_grace_time')

                if config.has_option('system', 'thread_invoked_time'):
                    self.system_invoked_sleep_time = config.get('system', 'thread_invoked_time')
                if config.has_option('system', 'thread_continuous_time'):
                    self.system_continuos_sleep_time = config.get('system', 'thread_continuous_time')

            if config.has_section('zabbix'):
                self.have.append('zabbix')
                if config.has_option('config', 'config'):
                    self.zabbix_cfg_file = config.get('zabbix', 'config')
                self.zabbix_sender = config.get('zabbix', 'zabbix_sender_path')
                self.zabbix_server = config.get('zabbix', 'zabbix_server')

            if config.has_section('network'):
                self.have.append('network')
                if config.has_option('network', 'BigIP_Enable'):
                    self.have.append('bigip')
                    self.network_bigip_enabled = config.getboolean('network', 'bigip_enable')
                    if self.network_bigip_enabled == True:
                        self.network_bigip_address = config.get('network', 'bigip_address')
                        self.network_bigip_user_name = config.get('network', 'bigip_user_name')
                        self.networl_bigip_user_password = config.get('network', 'bigip_user_password')
                else:
                    self.network_bigip_enabled = False


        except Exception, e:
            print e