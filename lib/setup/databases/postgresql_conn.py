import psycopg2
from lib.setup.Load import log
from lib.setup.databases.PGSQL_Tools import conf_anysize2byte


class PostgreSQL_Connect(object):
    user = None
    self.database = None
    password = None
    port = None
    host = None
    socket = None
    raw_value = None

    __conn__ = None

    def __init__(self, user=None, password=None, host=None, database=None, port=None, socket=None):
        self.user = user
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.socket = socket
        self.raw_value = None


    def pgsql_connect(self):
        try:
            self.__conn__ = psycopg2.connect(database=self.database, user=self.user, password=self.password,
                                             host=self.host, port=self.port)
        except psycopg2.DatabaseError, e:
            log.debug("Error on connect database: %s" % (e))
            log.debug("Error on MySQL with user %s host %s, database %s and socket %s" % (
                self.user, str(self.host), str(self.database), str(self.socket)))


    def pgsql_ping(self):
        try:
            cur = self.__conn__.cursor()
            cur.execute("select 1")
            row = cur.fetchone()
            cur.close()
            return 1
        except psycopg2.DatabaseError, e:
            log.debug("PostgreSQL ping fail")
            return 0

    def pgsql_execute(self, query):
        cur = self.__conn__.cursor()
        cur.execute(query)
        row = cur.fetchone()
        print row
        for row in cur.fetchall():
            status[row['Variable_name'].lower()] = row['Value']
        cur.close()
        return status


    def pgsql_verion_text(self):
        status = self.pgsql_execute("SELECT version();")
        return status.version


    def pgsql_verion_tuple(self):
        version_list = []
        status = self.pgsql_execute("SELECT version();")
        version = status.version.strip(' ')[1]
        version_list[version.strip('.')[1], version.strip('.')[2], version.strip('.')[3]]
        return tuple(version_list)

    ''' Show postgresql.conf '''

    def pgsql_show_all(self):
        pg_version = self.pgsql_verion_tuple()
        rs = self.pgsql_execute("show all")
        return conf_anysize2byte(rs, pg_version)

    ''' Another way to show postgresql.conf '''

    def pgsql_pg_setting(self):
        QUERY = "SELECT name, setting FROM pg_settings;"
        rs = self.pgsql_execute(QUERY)
        return rs

    def pgsql_autovacuum_freeze_max_age(self):

        '''
          type              => 'percent',
          default_warning   => '90%',
          default_critical  => '95%',
          normal <=             '25%'
        '''
        QUERY = """
                SELECT freez,
                      txns,
                      ROUND(100*(txns/freez::float)) AS perc,
                      datname FROM (
                                    SELECT foo.freez::int,
                                           age(datfrozenxid) AS txns,
                                           datname
                                    FROM pg_database d
                                    JOIN (SELECT setting AS freez FROM pg_settings WHERE name = 'autovacuum_freeze_max_age') AS foo
                                    ON (true) WHERE d.datallowconn
                                   )
                AS foo2 ORDER BY 3 DESC, 4 ASC;
            """
        status = self.pgsql_execute(QUERY)
        return status

    def pgsql_last_vacuum(self):
        status = None
        '''
        ltime = second between last and now()
        ptime = time of last
        '''
        QUERY = """
                SELECT  current_database() AS datname,
	                    nspname AS sname,
	                    relname AS tname,
                        CASE WHEN v IS NULL THEN
                                -1
                        ELSE
                            round(extract(epoch FROM now()-v))
                        END AS ltime,
                        CASE WHEN v IS NULL THEN
                            '?'
                        ELSE
                            TO_CHAR(v, 'HH24:MI FMMonth DD, YYYY')
                        END AS ptime
                FROM (
                        SELECT  nspname,
                                relname,
                                GREATEST(pg_stat_get_last_vacuum_time(c.oid), pg_stat_get_last_autovacuum_time(c.oid)) AS v
                        FROM pg_class c, pg_namespace n
                        WHERE relkind = 'r'
                        AND n.oid = c.relnamespace
                        AND n.nspname <> 'information_schema'
                        ORDER BY 3
                    ) AS foo
                """
        status = self.pgsql_execute(QUERY)
        return status

    def pgsql_last_analyze(self):
        status = None
        '''
        ltime = second between last and now()
        ptime = time of last
        '''
        QUERY = """
                SELECT  current_database() AS datname,
	                    nspname AS sname,
	                    relname AS tname,
                        CASE WHEN v IS NULL THEN
                                -1
                        ELSE
                            round(extract(epoch FROM now()-v))
                        END AS ltime,
                        CASE WHEN v IS NULL THEN
                            '?'
                        ELSE
                            TO_CHAR(v, 'HH24:MI FMMonth DD, YYYY')
                        END AS ptime
                FROM (
                        SELECT  nspname,
                                relname,
                                GREATEST(pg_stat_get_last_analyze_time(c.oid), pg_stat_get_last_autoanalyze_time(c.oid)) AS v
                        FROM pg_class c, pg_namespace n
                        WHERE relkind = 'r'
                        AND n.oid = c.relnamespace
                        AND n.nspname <> 'information_schema'
                        ORDER BY 3
                    ) AS foo
            """
        status = self.pgsql_execute(QUERY)
        return status


