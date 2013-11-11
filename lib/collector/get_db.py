'''
Created on 02/10/2013

@author: csmanioto
'''

from lib.setup.Load import have_section, db_mysql_modules, CACHE_FILE_INVOKED, CACHE_FILE_CONTINUOUS
from lib.setup.Header import CONS_COLLECT_FOR
from lib.collector.base.dbcheck.MySQL import MySQLCollector
#from lib.collector.base.dbcheck.PostgreSQL import PostgreSQLCollector
#from lib.collector.base.dbcheck.SQLServer import SQLServerCollector



class GetDB(object):
    filename = None
    priority = None

    def __del__(self):
        pass

    def __init__(self, priority):
        self.priority = priority
        if priority == CONS_COLLECT_FOR["INVOKED"]:
            self.filename = CACHE_FILE_INVOKED
        elif priority == CONS_COLLECT_FOR["CONTINUOUS"]:
            self.filename = CACHE_FILE_CONTINUOUS

    def collect(self):

        if 'mysql' in have_section:
            mysql_collector = MySQLCollector(self.filename)

            for modules in db_mysql_modules:
                if modules.lower().strip() == 'common' or modules.lower().strip() == 'mysql' or modules.lower().strip() == 'basic':
                    mysql_collector.collect_show_variables(self.priority)
                    mysql_collector.collect_size_status(self.priority)
                    mysql_collector.collect_show_status(self.priority)
                    mysql_collector.collect_qps(self.priority)
                    mysql_collector.collect_mysql_memory_usage(self.priority)
                    mysql_collector.collect_mysql_tcp_stats(self.priority)
                    mysql_collector.collect_show_innodb_status(self.priority)
                    mysql_collector.collect_time(self.priority)

                if modules.lower().strip() == 'slave':
                    mysql_collector.collect_slave_status(self.priority)

                if modules.lower().strip() == 'master':
                    mysql_collector.collector_master_status(self.priority)
            mysql_collector.disconnect()

        if 'postgresql' in have_section:
            #postgresql_collector = PostgreSQLCollector(self.filename)
            pass

        if 'sqlserver' in have_section:
            #sqlserver_collector = SQLServerCollector(self.filename)
            pass