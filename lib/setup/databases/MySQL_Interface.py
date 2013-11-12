'''
Created on 01/10/2013

@author: csmanioto
'''

from lib.setup.databases.mysql_conn import *
from lib.collector.base.oscheck.OS import *
from lib.common.powertools import convert_dict_to_object, convert_bool_to_int, kbytes2bytes, dict_key2lower, fixfloat
from lib.setup.Header import CONS_RAM_SERVER


class MySQL_Interface():
    '''
    classdocs
    '''

    def __init__(self, user, password, host, database, socket=None):
        pass
        self.__my_conn = MySQLConnect(user, password, host, database, socket)

    '''
        Metods
    '''

    def disconnect(self):
        self.__my_conn.mysql_close_connect()

    double_check = False

    def get_mysql_ping(self):
        try:
            isconnect = self.__my_conn.mysql_isconnected()
            if convert_bool_to_int(isconnect) == 1:
                return 1
            else:
                if not self.double_check:
                    try:
                        self.__my_conn.mysql_connect()
                        self.double_check = True
                        self.get_mysql_ping()
                    except:
                        pass
                else:
                    return 0
        except:
            return 0


    def get_mysql_version(self):
        try:
            return self.__my_conn.mysql_version_tuple()
        except:
            return None

    def get_show_status(self):
        my_dic = self.__my_conn.mysql_show_status()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None


    def get_show_variables(self):
        my_dic = self.__my_conn.mysql_show_variables()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None


    def get_show_slave_status(self):
        my_dic = self.__my_conn.mysql_slave_status()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None


    def get_show_master_status(self):
        my_dic = self.__my_conn.mysql_master_status()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None

    def get_show_innodb_status(self):
        my_dic = self.__my_conn.mysql_show_engine_innodb_status()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None

    def get_now(self):
        my_dic = self.__my_conn.mysql_get_now()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None


    def get_databases_status(self):
        my_dic = self.__my_conn.mysql_show_database_usage_status()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None

    def get_gpq(self):
        my_dic = self.__my_conn.mysql_query_per_second()
        if my_dic != None:
            return convert_dict_to_object(dict_key2lower(my_dic))
        else:
            return None

    def get_mysql_mem_usage(self):
        my_dic = {}
        os_get = OS(None)
        mysql_usage = self.__my_conn.mysql_memory_usage()
        meminfo = os_get.get_mem_info()
        try:
            ram = long(kbytes2bytes(meminfo.memtotal)) # bytes
            if ram < mysql_usage:
                ram = CONS_RAM_SERVER # 128 GB Ram
        except:
            ram = CONS_RAM_SERVER # 128 GB Ram

        my_dic['mysql_usage'] = fixfloat(round(mysql_usage, 2))  #bytes
        my_dic['usage_ram_free_size'] = fixfloat(round(ram - mysql_usage, 2))
        my_dic['usagem_ram_percent'] = fixfloat(round(mysql_usage * 100 / ram, 2))
        return convert_dict_to_object(dict_key2lower(my_dic))

        #return status

    def get_mysql_tcp_state(self):
        my_dic = {}
        os_get = OS(None)
        variables = self.__my_conn.mysql_show_variables()
        try:
            timewait = os_get.get_tcp_status(variables['port'], 'TIME_WAIT')
            established = os_get.get_tcp_status(variables['port'], 'ESTABLISHED')
        except:
            timewait = 0
            established = 0
        my_dic['time_wait'] = timewait
        my_dic['established'] = established
        return convert_dict_to_object(dict_key2lower(my_dic))

    def get_mysql_memory_report(self):
        my_dic = {}
        variables = self.__my_conn.mysql_show_variables()
        pid_file = variables['pid_file']
        os_get = OS(None)
        try:
            my_dic = os_get.get_pid_memory_info(None, pid_file)
            if my_dic != None:
                return convert_dict_to_object(dict_key2lower(my_dic))
            else:
                return None
        except:
            pass
            

