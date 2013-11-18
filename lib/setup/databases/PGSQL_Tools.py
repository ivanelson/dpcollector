__author__ = 'csmanioto'


def conf_anysize2byte(dict_data, pgsql_version_tuple=(8, 3, 0)):
    if pgsql_version_tuple > (8, 3, 0):
        status = None

    return status