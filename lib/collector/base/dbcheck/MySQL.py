'''
Created on 10/10/2013

@author: root
'''

import time

from lib.setup.Header import CONS_COLLECT_FOR
from lib.common.powertools import convert_bool_to_int, convert_now2unixtime, fix_time_now, get_unixtime_ntp_server
from lib.setup.databases.MySQL_Interface import MySQL_Interface
from lib.collector.base.WriteCache import WriteCache
from lib.setup.Load import db_mysql_user, db_mysql_password, db_mysql_hostname, db_mysql_socket, log, host_name, ntp_server, ntp_grace_time
from lib.collector.base.oscheck.OS import MetaOS


class MySQLCollector(object):
    '''
    classdocs
    '''

    mysqldb = None
    wcache = None
    datadir = None

    def __init__(self, filename):
        self.mysqldb = MySQL_Interface(db_mysql_user, db_mysql_password, db_mysql_hostname, 'mysql', db_mysql_socket)
        self.wcache = WriteCache(host_name, filename)

    def disconnect(self):
        self.mysqldb.disconnect()


    def write_key(self, key, value, ts=str(int(time.time()))):
        log.debug("get: %s" % key)
        self.wcache.toWrite(key, value, ts)

    def collect_show_status(self, priority):
        ts = str(int(time.time()))
        ''' show status '''
        status = self.mysqldb.get_show_status()
        #http://dev.mysql.com/doc/refman/5.1/en/server-status-variables.html#statvar_Com_xxx
        self.write_key("db.mysql.ping", self.mysqldb.get_mysql_ping(), ts)
        if bool(self.mysqldb.get_mysql_ping()):
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                self.write_key("db.mysql.show_status.network.sent", status.bytes_sent, ts)
                self.write_key("db.mysql.show_status.network.received", status.bytes_received, ts)
                self.write_key("db.mysql.show_status.max_used_connections", status.max_used_connections, ts)
                self.write_key("db.mysql.show_status.aborted_clients", status.aborted_clients, ts)
                self.write_key("db.mysql.show_status.number_select", status.com_select, ts)
                self.write_key("db.mysql.show_status.number_select_qcache", status.qcache_hits, ts)
                self.write_key("db.mysql.show_status.number_querys_cached", status.qcache_inserts, ts)
                self.write_key("db.mysql.show_status.number_insert", status.com_insert, ts)
                self.write_key("db.mysql.show_status.number_insert_select", status.com_insert_select, ts)
                self.write_key("db.mysql.show_status.number_update", status.com_update, ts)
                self.write_key("db.mysql.show_status.number_update_multi", status.com_update_multi, ts)
                self.write_key("db.mysql.show_status.number_delete", status.com_delete, ts)
                self.write_key("db.mysql.show_status.number_delete_multi", status.com_delete, ts)
                self.write_key("db.mysql.show_status.number_replace", status.com_replace, ts)
                self.write_key("db.mysql.show_status.number_replace_select", status.com_replace_select, ts)
                self.write_key("db.mysql.show_status.number_rollback", status.com_rollback, ts)
                self.write_key("db.mysql.show_status.number_call_procedure", status.com_call_procedure, ts)
                self.write_key("db.mysql.show_status.connected_user", status.threads_connected, ts)
                self.write_key("db.mysql.show_status.connected_user_running", status.threads_running, ts)
                self.write_key("db.mysql.show_status.aborted_connects", status.aborted_connects, ts)
                self.write_key("db.mysql.show_status.created_tmp_files", status.created_tmp_files, ts)
                self.write_key("db.mysql.show_status.created_tmp_disk_tables", status.created_tmp_disk_tables, ts)
                self.write_key("db.mysql.show_status.created_tmp_tables", status.created_tmp_tables, ts)
                self.write_key("db.mysql.show_status.innodb_rows_inserted", status.innodb_rows_inserted, ts)
                self.write_key("db.mysql.show_status.innodb_rows_deleted", status.innodb_rows_deleted, ts)
                self.write_key("db.mysql.show_status.innodb_rows_updated", status.innodb_rows_updated, ts)
                self.write_key("db.mysql.show_status.innodb_rows_read", status.innodb_rows_read, ts)
                ''' -------
                    INNODB STATUS (show status)
                    ------ 
                '''
                self.write_key("db.mysql.show_status.innodb_data_writes", status.innodb_data_writes, ts)
                self.write_key("db.mysql.show_status.innodb_data_written", status.innodb_data_written, ts)
                self.write_key("db.mysql.show_status.innodb_data_reads", status.innodb_data_reads, ts)
                self.write_key("db.mysql.show_status.innodb_data_read", status.innodb_data_read, ts)
                self.write_key("db.mysql.show_status.innodb_data_read", status.innodb_data_read, ts)
                self.write_key("db.mysql.show_status.innodb_page_size", status.innodb_page_size, ts)


    def collect_show_variables(self, priority=1):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            ''' Show Variables Status '''
            status = self.mysqldb.get_show_variables()
            self.datadir = status.datadir
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                self.write_key("db.mysql.show_variables.cfg_max_connections", status.max_connections, ts)
                self.write_key("db.mysql.show_variables.version", status.version, ts)
                self.write_key("db.mysql.show_variables.datadir", self.datadir, ts)


    def collect_mysql_memory_usage(self, priority=1):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            ''' Show Variables Status '''
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                status = self.mysqldb.get_mysql_mem_usage()

                self.write_key("db.mysql.mem_usage", status.mysql_usage, ts)
                self.write_key("db.mysql.mem_usage_free_size", status.usage_ram_free_size, ts)
                self.write_key("db.mysql.mem_usage_percent", status.usagem_ram_percent, ts)
                # status2
                try:
                    status2 = self.mysqldb.get_mysql_memory_report()
                    self.write_key("db.mysql.os_vm_usage", status2.vmsize, ts)
                    self.write_key("db.mysql.os_vm_resident", status2.vmrss, ts)
                    self.write_key("db.mysql.os_vm_swap_usage", status2.vmswap, ts)
                except:
                    pass


    def collect_size_status(self, priority=1):
        ts = str(int(time.time()))
        get_os = MetaOS()
        if bool(self.mysqldb.get_mysql_ping()):
            ''' Others Status '''

            ''' MySQL 5.1.x is very very slower to get SELECT sum(.... from information_schema.tables '''
            '''
            mysql_version = self.mysqldb.get_mysql_version()
            priority_select = None
            
            if mysql_version < (5,5,0):
                priority_select = CONS_COLLECT_FOR["INVOKED"]
            else:
                priority_select = CONS_COLLECT_FOR["CONTINUOUS"]
            '''
            total_data = 0
            number_database = 0
            file_system_used = 0

            if priority == CONS_COLLECT_FOR["INVOKED"]:
                try:
                    status = self.mysqldb.get_databases_status()
                    total_data = status.total_data
                    number_database = status.number_database
                except:
                    pass

                self.write_key("db.mysql.total_size", total_data, ts)
                self.write_key("db.mysql.number_database", number_database, ts)

            ''' get file usage on Operational System viwer '''
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                try:
                    file_system_used = get_os.get_folder_size(self.datadir)
                except:
                    pass

                self.write_key("db.mysql.filesystem_used", file_system_used, ts)

    def collect_slave_status(self, priority=2):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                ''' show slave status '''
                status = self.mysqldb.get_show_slave_status()
                self.write_key("db.mysql.slave_lagging", status.seconds_behind_master, ts)
                self.write_key("db.mysql.slave_io_thread", convert_bool_to_int(status.slave_io_running), ts)
                self.write_key("db.mysql.slave_sql_thread", convert_bool_to_int(status.slave_sql_running), ts)
                self.write_key("db.mysql.slave_error_number", status.last_errno, ts)
                self.write_key("db.mysql.slave_error", str(status.last_error).replace("", " "), ts)
                self.write_key("db.mysql.slave_master_log_file", str(status.master_log_file), ts)
                self.write_key("db.mysql.slave_read_master_log_pos", str(status.read_master_log_pos), ts)
                self.write_key("db.mysql.slave_relay_log_file", str(status.relay_log_file), ts)
                self.write_key("db.mysql.slave_relay_log_pos", str(status.relay_log_pos), ts)
                self.write_key("db.mysql.slave_relay_master_log_file", str(status.relay_master_log_file), ts)
                # Log Lagging
                master_log_file = long(str(status.master_log_file).split('.')[1])
                relay_master_log_file = long(str(status.relay_master_log_file).split('.')[1])
                log_laggin = master_log_file - relay_master_log_file
                self.write_key("db.mysql.slave_relay_log_lagging", log_laggin, ts)

    def collector_master_status(self, priority=1):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            if priority == CONS_COLLECT_FOR["INVOKED"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                status = self.mysqldb.get_show_master_status()
                try:
                    self.write_key("db.mysql.master_file", status.file, ts)
                except:
                    self.write_key("db.mysql.master_file", 'None', ts)

                try:
                    self.write_key("db.mysql.master_position", status.position, ts)
                except:
                    self.write_key("db.mysql.master_position", 'None', ts)


    def collect_show_innodb_status(self, priority=1):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                status = self.mysqldb.get_show_innodb_status()
                try:
                    self.write_key("db.mysql.innodb_srv_master_thread_log", status.innodb_srv_master_thread_log, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_os_wait_reservation_count", status.innodb_os_wait_reservation_count,
                                   ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_os_wait_signal_count", status.innodb_os_wait_signal_count, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_mutex_spin_waits", status.innodb_mutex_spin_waits, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_mutex_spin_rounds", status.innodb_mutex_spin_rounds, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_mutex_spin_os_waits", status.innodb_mutex_spin_os_waits, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_rw_shared_spins", status.innodb_rw_shared_spins, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_rw_shared_os_waits", status.innodb_rw_shared_os_waits, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_rw_excl_spins", status.innodb_rw_excl_spins, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_rw_excl_os_waits", status.innodb_rw_excl_os_waits, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_spin_rounds_per_wait_mutex",
                                   status.innodb_spin_rounds_per_wait_mutex, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_spin_rounds_per_wait_rw_shared",
                                   status.innodb_spin_rounds_per_wait_rw_shared, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_spin_rounds_per_wait_rw_excl",
                                   status.innodb_spin_rounds_per_wait_rw_excl, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_lastest_deadlock", status.innodb_lastest_deadlock, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_file_read", status.innodb_file_read, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_file_write", status.innodb_file_write, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_file_fsync", status.innodb_file_fsync, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_iops_read", status.innodb_iops_read, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_read_bytes_seconds", status.innodb_read_bytes_seconds, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_ios_write", status.innodb_ios_write, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_fsyncs_seconds", status.innodb_fsyncs_seconds, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_insert_buffer_size", status.innodb_insert_buffer_size, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_insert_buffer_number", status.innodb_insert_buffer_number, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_insert_buffer_merged", status.innodb_insert_buffer_merged, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_insert_buffer_merges", status.innodb_insert_buffer_merges, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_insert_hash_searches_seconds",
                                   status.innodb_insert_hash_searches_seconds, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_insert_non_hash_searches_seconds",
                                   status.innodb_insert_non_hash_searches_seconds, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_log_sequence_number", status.innodb_log_sequence_number, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_log_sequence_number", status.innodb_log_sequence_number, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_log_iops", status.innodb_log_iops, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_total_memory_allocated", status.innodb_total_memory_allocated, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_additional_pool_allocated", status.innodb_additional_pool_allocated,
                                   ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_dictinoary_memory_allocated",
                                   status.innodb_dictinoary_memory_allocated, ts)
                except:
                    pass
                try:
                    buffer_pool = status.innodb_page_buffer_pool_size
                    self.write_key("db.mysql.innodb_page_buffer_pool_size", buffer_pool, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_free_buffers", status.innodb_free_buffers, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_database_pages", status.innodb_database_pages, ts)
                except:
                    pass
                try:
                    self.write_key("db.mysql.innodb_old_database_pages", status.innodb_old_database_pages, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_modified_db_pages", status.innodb_modified_db_pages, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pending_reads", status.innodb_pending_reads, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pending_write_lru", status.innodb_pending_write_lru, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pending_write_flush_list", status.innodb_pending_write_flush_list,
                                   ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pending_write_single_page", status.innodb_pending_write_single_page,
                                   ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_made_young", status.innodb_pages_made_young, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_made_not_young", status.innodb_pages_made_not_young, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_young_seconds", status.innodb_pages_young_seconds, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_non_young_seconds", status.innodb_pages_non_young_seconds, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_read", status.innodb_pages_read, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_created", status.innodb_pages_created, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_written", status.innodb_pages_written, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_read_seconds", status.innodb_pages_read_seconds, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_created_seconds", status.innodb_pages_created_seconds, ts)
                except:
                    pass

                try:
                    self.write_key("db.mysql.innodb_pages_written_seconds", status.innodb_pages_written_seconds, ts)
                except:
                    pass
                    #print status

    def collect_qps(self, priority=1):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            status = self.mysqldb.get_gpq()
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                self.write_key("db.mysql.show_qps", status.qps, ts)


    def collect_mysql_tcp_stats(self, priority=1):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            status = self.mysqldb.get_mysql_tcp_state()
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                self.write_key("db.mysql.tcp_timewait", status.time_wait, ts)
                self.write_key("db.mysql.tcp_established", status.established, ts)

    def collect_time(self, priority=1):
        ts = str(int(time.time()))
        if bool(self.mysqldb.get_mysql_ping()):
            status = self.mysqldb.get_now()
            if priority == CONS_COLLECT_FOR["CONTINUOUS"] or priority == CONS_COLLECT_FOR["BOOTH"]:
                try:
                    self.write_key("db.mysql.time_now", fix_time_now(status.now), ts)
                    self.write_key("db.mysql.timezone", status.timezone, ts)
                    self.write_key("db.mysql.time_unixtime", convert_now2unixtime(status.now), ts)
                    mysql_time = int(convert_now2unixtime(status.now))
                except:
                    mysql_time = 0
                if mysql_time is not None and mysql_time > 0:
                    ntp_time = get_unixtime_ntp_server(ntp_server)
                    time_error = ntp_time - (mysql_time + 3)

                    if time_error > int(ntp_grace_time * -1) and time_error < int(
                                    ntp_grace_time * 1): # Time grace - Delay between get now() and get ntp date
                        time_error = 0
                    if time_error is not None:
                        self.write_key("db.mysql.time_unixtime_ntp_time", time_error, ts)

    def collect_all(self, priority):
        self.collect_show_innodb_status(priority)
        self.collect_show_status(priority)
        self.collect_show_variables(priority)
        self.collect_size_status(priority)
        self.collect_slave_status(priority)
        self.collector_master_status(priority)
        self.collect_time(priority)
        self.disconnect()