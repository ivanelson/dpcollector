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

    def pgsql_show_all(self):
        pg_version = self.pgsql_verion_tuple()
        rs = self.pgsql_execute("show all")
        return conf_anysize2byte(rs, pg_version)
