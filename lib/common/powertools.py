'''
Created on 16/09/2013

@author: csmanioto
'''

from __future__ import with_statement
import socket
import logging
import re
import struct
import datetime
import time

import ntplib

from lib.setup.Header import CONS_NTP_SERVER




#from types import *
#from sys import getsizeof
#from inspect import getmembers
#from collections import (deque, defaultdict, Counter, OrderedDict, Iterable)



def parse_config_file(arquivo, COMMENT_CHAR='#', OPTION_CHAR='='):
    options = {}
    try:
        with open(arquivo) as myfile:
            for line in myfile:
                if COMMENT_CHAR in line:
                    # split on comment char, keep only the part before
                    #line, comment = line.split(COMMENT_CHAR, 1)
                    continue
                if OPTION_CHAR in line:
                    option, value = line.split(OPTION_CHAR, 1)
                    option = option.strip()
                    #value = value.sdatetime.date.today().strip()
                    options[option] = value
        return convert_dict_to_object(options)
    except:
        return None


def convert_dict_to_object(dic):
    top = type('new', (object,), dic)
    seqs = tuple, list, set, frozenset
    for i, j in dic.items():
        if isinstance(j, dict):
            setattr(top, i, convert_dict_to_object(j))
        elif isinstance(j, seqs):
            setattr(top, i,
                    type(j)(convert_dict_to_object(sj) if isinstance(sj, dict) else sj for sj in j))
        else:
            setattr(top, i, j)
    return top


def get_value_constant(value, constant):
    return constant.get(value)


def get_tcp_v4_ip2host(ip_address):
    return socket.gethostbyaddr(ip_address[0])


def get_tcp_v4_host2ip(hostname):
    return socket.gethostbyaddr(hostname[1])


def get_loggin_level(level="DEBUG"):
    if level == 'INFO':
        return logging.INFO

    if level == 'WARN':
        return logging.WARN

    if level == 'DEBUG':
        return logging.DEBUG

    if level == 'ERROR':
        return logging.ERROR

    if level == 'CRITCAL':
        return logging.CRITICAL


from math import log

unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])


def sizeof_fmt(num):
    """Human friendly file size"""
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024 ** exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'


def cursor_to_dict(cursor):
    data = cursor.fetchone()
    if data == None:
        return None
    desc = cursor.description
    for (name, value) in zip(desc, data):
        dict[name[0]] = value
    return dict


def convert2bool(value):
    if type(value) == type(int()) or type(long()):
        if value == 1:
            return True
        else:
            return False

    if type(value) == type(str()) or type(unicode()):
        if value.lower() == "yes" or value.lower() == "true" or value == "1":
            return True
        else:
            return False


def convert_bool_to_int(value):
    if type(value) == type(bool()):
        if value:
            return 1
        else:
            return 0
    if type(value) == type(str()) or type(unicode()):
        if value.lower() == "yes" or value.lower() == "true" or value == "1":
            return 1
        else:
            return 0


def printit(stats, rs):
    # print rs
    for t in rs:
        k = t[1]
        v = t[2]
        # print k, v
        if stats.has_key(k):
            oldv = stats[k]
            try:
                vi = int(v)
                match = re.match("cachetable size|txn oldest live|next LSN|.*in use|.*footprint", k)
                if match:
                    if v != oldv: print
                    k, v, '*'
                else:
                    di = vi - int(oldv)
                    if di: print
                    k, di
            except:
                if v != oldv: print
                k, v
        stats[k] = v
    print


def bytes2mega(byte):
    giga = 1048576 #Bytes
    size = long(byte) / long(giga)
    if size > 0:
        return round(size, 2)


def kbytes2mega(kbyte):
    giga = 1024 #Bytes
    size = long(kbyte) / long(giga)
    if size > 0:
        return round(size, 2)


def kbytes2bytes(kbyte):
    byte = 1024 #Bytes
    size = long(kbyte) * long(byte)
    if size > 0:
        return long(round(size, 2))
    else:
        return 0


def kbytes2giga(kbyte):
    giga = 1048576 #Bytes
    size = long(kbyte) / long(giga)
    if size > 0:
        return round(size, 2)


def mega2giga(mega):
    giga = 1024 #Bytes
    size = long(mega) / long(giga)
    if size > 0:
        return round(size, 2)


def mega2byte(mega):
    byte = 1048576 #Bytes 1024^2
    size = long(mega) / long(byte)
    if size > 0:
        return round(size, 2)


def bytes2giga(byte):
    giga = 1073741824 #Bytes
    size = long(byte) / long(giga)
    if size > 0:
        return round(size, 2)
    else:
        return 0


def dict_key2lower(my_dic):
    status = {}
    for key, value in my_dic.items():
        status[key.lower()] = value
    return status


def get_unixtime_ntp_server(ntp_server=CONS_NTP_SERVER):
    c = ntplib.NTPClient()
    response = c.request(ntp_server)
    try:
        unixtimestamp = int(response.tx_time)
        return unixtimestamp
    except:
        unixtimestamp = int(time.time())
        return unixtimestamp


def fix_time_now(now_s):
    regex_now = r"\d+-\d+-\d+ \d+:\d+:\d+" #  date format - 2013-10-16 13:03:03
    return re.search(regex_now, str(now_s)).group()


def convert_now2unixtime(now_s):
    now_re = fix_time_now(now_s[0])
    split_date = str(now_re).split(' ')[0]
    split_time = str(now_re).split(' ')[1]

    year = int(split_date.split('-')[0])
    month = int(split_date.split('-')[1])
    day = int(split_date.split('-')[2])

    hour = int(split_time.split(':')[0])
    minute = int(split_time.split(':')[1])
    seconds = int(split_time.split(':')[2])

    dt = datetime.datetime(year, month, day, hour, minute, seconds)
    return int(time.mktime(dt.timetuple()))


def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


def long2ip(ip_long):
    return socket.inet_ntoa(struct.pack('!L', long(ip_long))).strip()


def fixfloat(f):
    '''
    Thanks Zachary Weinberg - owlfolio.org - Author of this Function
    '''

    ftod_r = re.compile(br'^(-?)([0-9]*)(?:\.([0-9]*))?(?:[eE]([+-][0-9]+))?$')

    """Print a floating-point number in the format expected by PDF:
    as short as possible, no exponential notation."""

    s = bytes(str(f))
    m = ftod_r.match(s)
    if not m:
        raise RuntimeError("unexpected floating point number format: {!a}".format(s))
    sign = m.group(1)
    intpart = m.group(2)
    fractpart = m.group(3)
    exponent = m.group(4)

    if ((intpart is None or intpart == b'') and
            (fractpart is None or fractpart == b'')):
        raise RuntimeError("unexpected floating point number format: {!a}".format(s))

    # strip leading and trailing zeros
    if intpart is None:
        intpart = b''
    else:
        intpart = intpart.lstrip(b'0')
    if fractpart is None:
        fractpart = b''
    else:
        fractpart = fractpart.rstrip(b'0')

    if intpart == b'' and fractpart == b'':
        # zero or negative zero; negative zero is not useful in PDF
        # we can ignore the exponent in this case
        return b'0'

    # convert exponent to a decimal point shift
    elif exponent is not None:
        exponent = int(exponent)
        exponent += len(intpart)
        digits = intpart + fractpart
        if exponent <= 0:
            return sign + b'.' + b'0' * (-exponent) + digits
        elif exponent >= len(digits):
            return sign + digits + b'0' * (exponent - len(digits))
        else:
            return sign + digits[:exponent] + b'.' + digits[exponent:]

    # no exponent, just reassemble the number
    elif fractpart == b'':
        return sign + intpart # no need for trailing dot
    else:
        return sign + intpart + b'.' + fractpart