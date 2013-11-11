'''
Created on 06/10/2013

@author: csmanioto
'''
import mysql.connector
from lib.setup.Load import log
from lib.setup.databases.MySQL_Tools import parse_innodb_status
from lib.setup.Header import MYSQL_CONNECTION_TIMEOUT


class MySQLCursorDict(mysql.connector.cursor.MySQLCursor):
    '''http://geert.vanderkelen.org/connectorpython-custom-cursors/'''
    # in mysql.connector.cursor.MySQLCursor
    tuple_factory = tuple

    def _row_to_python(self, rowdata, desc=None):
        my_dic = {}
        row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
        if row:
            my_dic = dict(zip(self.column_names, row))
            return my_dic
        return None

    def fetchone(self):
        row = self._fetch_row()
        if row:
            return dict(zip(self.column_names, self._row_to_python(row)))
        return None


class MySQLConnect(object):
    '''
    classdocs
    '''
    __conx = None
    __cursor = None
    __custom_cursor = None
    log = None

    user = None
    password = None
    host = None
    database = None
    socket = None
    raw_value = None

    def mysql_connect(self):
        try:
            if self.socket:
                self.__conx = mysql.connector.connect(user=self.user, password=self.password, host=self.host,
                                                      unix_socket=self.socket, database='mysql', raw=self.raw_value,
                                                      connection_timeout=MYSQL_CONNECTION_TIMEOUT)
            else:
                self.__conx = mysql.connector.connect(user=self.user, password=self.password, host=self.host,
                                                      database='mysql', raw=self.raw_value,
                                                      connection_timeout=MYSQL_CONNECTION_TIMEOUT)
        except Exception, e:
            log.debug("Error on connect database: %s" % (e))
            log.debug("Error on MySQL with user %s host %s, database %s and socket %s" % (
            self.user, str(self.host), str(self.database), str(self.socket)))

    def __init__(self, user, password, host, database, socket=None, raw_value=None):
        self.user = user
        self.password = password
        self.host = host
        self.socket = socket
        self.raw_value = None

        self.mysql_connect()
        self.user = user
        self.password = password
        self.database = database
        self.socket = socket

    def mysql_get_connect(self):
        return self.__conx

    def mysql_close_connect(self):
        try:
            self.__conx.close()
            return True
        except:
            return False

    def mysql_send_ping(self):
        return self.__conx.cmd_ping()

    def mysql_version_string(self):
        try:
            return self.__conx.get_server_info()
        except:
            log.debug("Error on get version")

    def mysql_version_tuple(self):
        try:
            return self.__conx.get_server_version()
        except:
            log.debug("Error on get version")

    def mysql_isconnected(self):
        try:
            return self.__conx.is_connected()
        except:
            return False
            log.debug("Error on get mysql test connect")

    def mysql_get_timezone(self):
        try:
            return self.__conx.get_time_zone()
        except:
            log.debug("Error on get timezone")

    def mysql_get_now(self):
        status = {}
        try:
            query = 'select now()'
            cur = self.__conx.cursor(raw=True)
            cur.execute(query)
            for row in cur.fetchall():
                status['now'] = row
            cur.close()
            status['timezone'] = self.mysql_get_timezone()
            return status
        except:
            return None

    def mysql_show_database_usage_status(self):
        status = {}
        if self.mysql_version_tuple() >= (5, 1, 0):
            try:
                query = 'SELECT COUNT(DISTINCT(table_schema)) as num_db,  CONCAT(sum(ROUND((CAST(DATA_LENGTH + INDEX_LENGTH AS SIGNED) - CAST(DATA_FREE AS SIGNED)),0))) AS size  FROM INFORMATION_SCHEMA.TABLES;'
                cursor = self.__conx.cursor(raw=True)
                cursor.execute(query)
                for row in cursor.fetchall():
                    status['number_database'] = row[0]
                    status['total_data'] = row[1]
            except Exception, e:
                log.debug("Error %s on execute %s" % (e, query))
                status['number_database'] = 0
                status['total_data'] = 0
                if not self.mysql_isconnected():
                    self.mysql_connect()

        else:
            status['number_database'] = 0
            status['total_data'] = 0
        return status

    def mysql_show_status(self):
        try:
            status = {}
            query = 'show  status;'
            cur = self.__conx.cursor(cursor_class=MySQLCursorDict)
            cur.execute(query)
            for row in cur.fetchall():
                status[row['Variable_name']] = row['Value']
            cur.close()
            return status
        except Exception, e:
            log.debug("Error %s on execute %s" % (e, query))

    def mysql_show_variables(self):
        try:
            status = {}
            query = 'show variables;'
            cur = self.__conx.cursor(cursor_class=MySQLCursorDict)
            cur.execute(query)
            for row in cur.fetchall():
                status[row['Variable_name'].lower()] = row['Value']
            cur.close()
            return status
        except Exception, e:
            log.debug("Error %s on execute %s" % (e, query))

    def mysql_memory_usage(self):
        show_variables = self.mysql_show_variables()
        ''' Global '''
        key_buffer_size = long(show_variables['key_buffer_size'])
        query_cache_size = long(show_variables['query_cache_size'])
        tmp_table_size = long(show_variables['tmp_table_size'])
        innodb_buffer_pool_size = long(show_variables['innodb_buffer_pool_size'])
        innodb_additional_mem_pool_size = long(show_variables['innodb_additional_mem_pool_size'])
        innodb_log_buffer_size = long(show_variables['innodb_log_buffer_size'])
        ''' Thread '''
        max_connection = long(show_variables['max_connections'])
        read_buffer_size = long(show_variables['read_buffer_size'])
        read_rnd_buffer_size = long(show_variables['read_rnd_buffer_size'])
        join_buffer_size = long(show_variables['join_buffer_size'])
        thread_stack = long(show_variables['thread_stack'])
        binlog_cache_size = long(show_variables['binlog_cache_size'])

        Global = key_buffer_size + query_cache_size + tmp_table_size + innodb_buffer_pool_size + innodb_additional_mem_pool_size + innodb_log_buffer_size
        PerThread = read_buffer_size + read_rnd_buffer_size + join_buffer_size + thread_stack + binlog_cache_size
        Total = Global + (max_connection * PerThread)
        #Total = bytes2giga(Total)
        return Total


    def mysql_query_per_second(self):
        try:
            status = {}
            query = "show status like 'Queries';"
            cur = self.__conx.cursor(cursor_class=MySQLCursorDict)
            cur.execute(query)
            qt1 = 0
            #qt2 = 0

            for row in cur.fetchall():
                qt1 = long(row['Value'])
            cur.close()
            #time.sleep(01)

            #cur = self.__conx.cursor(cursor_class=MySQLCursorDict)
            #cur.execute(query)
            #for row in cur.fetchall():
            #    qt2 = long(row['Value'])
            #cur.close()


            #status['qps'] = qt2 - qt1
            status['qps'] = qt1
            return status
        except Exception, e:
            log.debug("Error %s on execute %s" % (e, query))


    def mysql_master_status(self):
        try:
            query = 'show master status;'
            cur = self.__conx.cursor(cursor_class=MySQLCursorDict)
            cur.execute(query)
            for row in cur.fetchall():
                pass
            cur.close()
            return row
        except Exception, e:
            log.debug("Error %s on execute %s" % (e, query))

    def mysql_slave_status(self):
        try:
            query = 'show slave status;'
            cur = self.__conx.cursor(cursor_class=MySQLCursorDict)
            cur.execute(query)
            for row in cur.fetchall():
                pass
            cur.close()
            return row
        except Exception, e:
            log.debug("Error %s on execute %s" % (e, query))

    def mysql_show_engine_innodb_status(self):
        ''' Use MySQL_Utils '''
        rs = None
        try:
            query = 'show engine innodb status'
            cur = self.__conx.cursor()
            cur.execute(query)
            # MySQL 5.1 < fechone() is good but not work in 5.5 >
            for row in cur.fetchall():
                pass
            cur.close()
            retorno = parse_innodb_status(row, self.mysql_version_tuple())
            return retorno
        except Exception, e:
            log.debug("Error %s on execute %s" % (e, query))


    def mysql_execute(self, query):
        try:
            self.__connect(self.user, self.password, self.host, self.database, self.socket)
            cur = self.__conx.cursor()
            cur.execute(query)
            return cur
        except:
            log.debug("Error on execute %s" % query)
                
            