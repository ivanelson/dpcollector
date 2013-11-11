import re


# http://www.mysqlperformanceblog.com/2006/07/17/show-innodb-status-walk-through/
#http://gmond-python-modules.googlecode.com/svn-history/r33/trunk/mysql.py
# Used in re.search(regexp, string)
# 1.00 or +1.00 or -1.00 or +1 or -1 or 1 

i = 0
regex_float = r"[-+]?\d*\.\d+|[-+]?\d+"
regex_date_deadlock = r"^\d+ \d+:\d+:\d+$" # MySQL Log  date format - 130812 13:03:03

def parse_innodb_status(rs, mysql_version_tuple=(5, 1, 0)):
    '''
    -------------------------------------
    INSERT BUFFER AND ADAPTIVE HASH INDEX
    -------------------------------------
    Ibuf: size 16389, free list len 39469, seg size 55859,
    17078598 inserts, 16666750 merged recs, 3072866 merges
    Hash table size 63749393, node heap has 130085 buffer(s)
    25150.49 hash searches/s, 3233.24 non-hash searches/s
    '''
    result = {}
    #back_ground_collected = False
    #semaphores_collected = False
    #dead_lock_collected = False
    #hash_index_collected = False
    #log_collected = False 
    #buffer_pool_collected = False

    for line in rs:
        if not "INNODB MONITOR OUTPUT" in line:
            continue

        for subline in line.split('\n'):
            '''
            -----------------
            BACKGROUND THREAD
            -----------------
            srv_master_thread loops: 744407 1_second, 587828 sleeps, 74439 10_second, 3831 background, 3828 flush
            srv_master_thread log flush and writes: 601690
            '''

            if "srv_master_thread log flush and writes" in subline.split(':'):
                result['innodb_srv_master_thread_log'] = subline.split(':')[1]

            '''
            ----------
            SEMAPHORES
            ----------
            OS WAIT ARRAY INFO: reservation count 3579769, signal count 44060682
            Mutex spin waits 182547586, rounds 262769946, OS waits 1553789
            RW-shared spins 16313415, OS waits 1242324; RW-excl spins 999138, OS waits 649993
            Spin rounds per wait: 1.44 mutex, 4.27 RW-shared, 68.71 RW-excl
            '''

            if "OS WAIT ARRAY INFO" in subline:
                if mysql_version_tuple < (5, 5, 0):
                    result['innodb_os_wait_reservation_count'] = re.search(regex_float, subline.split(',')[0]).group()
                    result['innodb_os_wait_signal_count'] = re.search(regex_float, subline.split(',')[1]).group()
                else:
                    result['innodb_os_wait_reservation_count'] = re.search(regex_float, subline.split(':')[1]).group()
                    # result['innodb_os_wait_signal_count'] = re.search(regex_float, subline.split(',')[1]).group()

            if "Mutex spin waits" in subline:
                result['innodb_mutex_spin_waits'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_mutex_spin_rounds'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_mutex_spin_os_waits'] = re.search(regex_float, subline.split(',')[2]).group()

            if "RW-shared spins" in subline:
                if mysql_version_tuple < (5, 5, 0):
                    result['innodb_rw_shared_spins'] = re.search(regex_float,
                                                                 subline.split(';')[0].split(',')[0]).group()
                    result['innodb_rw_shared_os_waits'] = re.search(regex_float,
                                                                    subline.split(';')[0].split(',')[1]).group()
                    result['innodb_rw_excl_spins'] = re.search(regex_float, subline.split(';')[1].split(',')[0]).group()
                    result['innodb_rw_excl_os_waits'] = re.search(regex_float,
                                                                  subline.split(';')[1].split(',')[1]).group()
                else:
                    result['innodb_rw_shared_spins'] = re.search(regex_float, subline.split(',')[0]).group()
                    result['innodb_rw_shared_rounds'] = re.search(regex_float, subline.split(',')[1]).group()
                    result['innodb_rw_shared_os_waits'] = re.search(regex_float, subline.split(',')[2]).group()

            if "Spin rounds per wait" in subline:
                splited = subline.split(',')
                result['innodb_spin_rounds_per_wait_mutex'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_spin_rounds_per_wait_rw_shared'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_spin_rounds_per_wait_rw_excl'] = re.search(regex_float, subline.split(',')[2]).group()

            # ------------------------
            #DETECTED DEADLOCK
            #------------------------
            #if re.match(regex_date_deadlock, subline.split(',')[0].strip()) and not dead_lock_collected:
            if re.match(regex_date_deadlock, subline.split(',')[0].strip()):
                result['innodb_lastest_deadlock'] = subline.split(',')[0].strip()
                #dead_lock_collected = True

            '''
            --------
            FILE I/O
            --------
            I/O thread 0 state: waiting for i/o request (insert buffer thread)
            I/O thread 1 state: waiting for i/o request (log thread)
            I/O thread 2 state: waiting for i/o request (read thread)
            I/O thread 3 state: waiting for i/o request (read thread)
            I/O thread 4 state: waiting for i/o request (read thread)
            I/O thread 5 state: waiting for i/o request (read thread)
            I/O thread 6 state: waiting for i/o request (write thread)
            I/O thread 7 state: waiting for i/o request (write thread)
            I/O thread 8 state: waiting for i/o request (write thread)
            I/O thread 9 state: waiting for i/o request (write thread)
            Pending normal aio reads: 0, aio writes: 0,
            ibuf aio reads: 0, log i/o's: 0, sync i/o's: 0
            Pending flushes (fsync) log: 0; buffer pool: 0
            48934754 OS file reads, 98016035 OS file writes, 80186649 OS fsyncs
            80.18 reads/s, 16409 avg bytes/read, 220.99 writes/s, 193.61 fsyncs/s
            '''

            if "OS file writes" in subline:
                result['innodb_file_read'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_file_write'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_file_fsync'] = re.search(regex_float, subline.split(',')[2]).group()

            if "avg bytes/read" in subline:
                result['innodb_iops_read'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_read_avg_bytes_seconds'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_ios_write'] = re.search(regex_float, subline.split(',')[2]).group()
                result['innodb_fsyncs_seconds'] = re.search(regex_float, subline.split(',')[3]).group()

            '''
            -------------------------------------
            INSERT BUFFER AND ADAPTIVE HASH INDEX
            -------------------------------------
            Ibuf: size 16389, free list len 39469, seg size 55859,
            17078598 inserts, 16666750 merged recs, 3072866 merges
            Hash table size 63749393, node heap has 130085 buffer(s)
            25150.49 hash searches/s, 3233.24 non-hash searches/s
            '''
            if "Ibuf: size" in subline:
                result['innodb_insert_buffer_size'] = re.search(regex_float, subline.split(',')[0]).group()

            if "merged recs" in subline:
                result['innodb_insert_buffer_number'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_insert_buffer_merged'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_insert_buffer_merges'] = re.search(regex_float, subline.split(',')[2]).group()

            if "hash searches/s" in subline:
                result['innodb_insert_hash_searches_seconds'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_insert_non_hash_searches_seconds'] = re.search(regex_float,
                                                                              subline.split(',')[1]).group()

            '''
            ---
            LOG
            ---
            Log sequence number 46522008800894
            Log flushed up to   46522008800894
            Last checkpoint at  46521267853646
            0 pending log writes, 0 pending chkp writes
            76906070 log i/o's done, 161.17 log i/o's/second
            '''
            if "Log sequence number" in subline:
                result['innodb_log_sequence_number'] = re.search(regex_float, subline).group()

            if "Log flushed up to" in subline:
                result['innodb_log_sequence_number'] = re.search(regex_float, subline).group()

            if "log i/o's/second" in subline:
                result['innodb_log_iops'] = re.search(regex_float, subline.split(',')[1]).group()

            '''
            ----------------------
            BUFFER POOL AND MEMORY
            ----------------------
            Total memory allocated 32935772160; in additional pool allocated 0
            Dictionary memory allocated 11805597
            Buffer pool size   1966080
            Free buffers       62
            Database pages     1823145
            Old database pages 672976
            Modified db pages  326722
            Pending reads 0
            Pending writes: LRU 0, flush list 0, single page 0
            Pages made young 89284607, not young 0
            56.94 youngs/s, 0.00 non-youngs/s
            Pages read 65699025, created 23906397, written 71137348
            26.97 reads/s, 3.00 creates/s, 6.99 writes/s
            Buffer pool hit rate 1000 / 1000, young-making rate 0 / 1000 not 0 / 1000
            Pages read ahead 0.00/s, evicted without access 0.00/s, Random read ahead 0.00/s
            LRU len: 1823145, unzip_LRU len: 0
            I/O sum[3682]:cur[12], unzip sum[0]:cur[0]
            '''

            if "Total memory allocated" in subline:
                result['innodb_total_memory_allocated'] = re.search(regex_float, subline.split(';')[0]).group()
                result['innodb_additional_pool_allocated'] = re.search(regex_float, subline.split(';')[1]).group()

            if "Dictionary memory allocated" in subline:
                result['innodb_dictinoary_memory_allocated'] = re.search(regex_float, subline).group()

            if "Buffer pool size" in subline:
                result['innodb_page_buffer_pool_size'] = re.search(regex_float, subline).group()

            if "Free buffers" in subline:
                result['innodb_free_buffers'] = re.search(regex_float, subline).group()

            if "Database pages" in subline:
                result['innodb_database_pages'] = re.search(regex_float, subline).group()

            if "Old database pages" in subline:
                result['innodb_old_database_pages'] = re.search(regex_float, subline).group()

            if "Modified db pages" in subline:
                result['innodb_modified_db_pages'] = re.search(regex_float, subline).group()

            if "Pending reads" in subline:
                result['innodb_pending_reads'] = re.search(regex_float, subline).group()

            if "Pending writes" in subline:
                result['innodb_pending_write_lru'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_pending_write_flush_list'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_pending_write_single_page'] = re.search(regex_float, subline.split(',')[2]).group()

            if "Pages made young" in subline:
                result['innodb_pages_made_young'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_pages_made_not_young'] = re.search(regex_float, subline.split(',')[1]).group()

            if "youngs/s" in subline:
                result['innodb_pages_young_seconds'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_pages_non_young_seconds'] = re.search(regex_float, subline.split(',')[1]).group()

            if "Pages read" in subline:
                result['innodb_pages_read'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_pages_created'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_pages_written'] = re.search(regex_float, subline.split(',')[2]).group()

            if "creates/s" in subline:
                result['innodb_pages_read_seconds'] = re.search(regex_float, subline.split(',')[0]).group()
                result['innodb_pages_created_seconds'] = re.search(regex_float, subline.split(',')[1]).group()
                result['innodb_pages_written_seconds'] = re.search(regex_float, subline.split(',')[2]).group()

        #    break
        #break
        return result
            