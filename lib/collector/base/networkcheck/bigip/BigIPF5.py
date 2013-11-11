'''
Created on 03/10/2013

@author: csmanioto
'''
import pycontrol.pycontrol as pc
#https://devcentral.f5.com/wiki/iControl.APIReference.ashx

from lib.setup.Header import CONS_BIGIP_ENABLE
from lib.common.powertools import get_value_constant


class BigIPF5(object):
    '''
    classdocs
    '''
    #hostname = '10.80.5.4'  
    #username   = 'dba_monitor'
    #password   = 'db4_m0n1t0r',

    hostname = None
    username = None
    password = None

    def __init__(self, hostname, username, password):
        '''
        Constructor
        '''
        self.hostname = hostname
        self.username = username
        self.password = password


    def getAllPools(self):
        b = pc.BIGIP(hostname=self.hostname, username=self.username, password=self.password, fromurl=True,
                     wsdls=['LocalLB.Pool', 'GlobalLB.Pool'])
        pools = b.LocalLB.Pool.get_list()
        return pools

    def getAllMembersOfPool(self, poolname):
        b = pc.BIGIP(
            hostname=self.hostname.strip(),
            username=self.username.strip(),
            password=self.password.strip(),
            fromurl=True,
            wsdls=['LocalLB.PoolMember'])

        pm = b.LocalLB.PoolMember
        rawpmstatus = b.LocalLB.PoolMember.get_object_status(pool_names=[poolname])
        pmstatusdic = {}
        for i in rawpmstatus:
            for x in i:
                #k = "%s:%s" % (x.member.address, x.member.port)
                host = "%s" % x.member.address
                pmstatusdic.update({
                host: {'avail': x.object_status.availability_status, 'enabled': x.object_status.enabled_status,
                       'status_desc': x.object_status.status_description}})
        return pmstatusdic


    def getEnableMemberOfPool(self, poolname):
        b = pc.BIGIP(hostname=self.hostname, username=self.username, password=self.password, fromurl=True,
                     wsdls=['LocalLB.PoolMember'])
        pm = b.LocalLB.PoolMember
        rawpmstatus = pm.get_object_status(pool_names=[poolname])
        pmstatusdic = {}
        for i in rawpmstatus:
            for x in i:
                if x.object_status.enabled_status == CONS_BIGIP_ENABLE[0]:
                    pmstatusdic.update(x.member.address)
        return pmstatusdic


    def getDisableMemberOfPool(self, poolname):
        b = pc.BIGIP(hostname=self.hostname, username=self.username, password=self.password, fromurl=True,
                     wsdls=['LocalLB.PoolMember'])
        pm = b.LocalLB.PoolMember
        rawpmstatus = pm.get_object_status(pool_names=[poolname])
        pmstatusdic = {}
        for i in rawpmstatus:
            for x in i:
                if x.object_status.enabled_status != CONS_BIGIP_ENABLE[0]:
                    pmstatusdic.update(x.member.address)
        return pmstatusdic


        def getStatusOfMember(self, poolname, ip_address):
            b = pc.BIGIP(hostname=self.hostname, username=self.username, password=self.password, fromurl=True,
                         wsdls=['LocalLB.PoolMember'])
            pm = b.LocalLB.PoolMember
            rawpmstatus = pm.get_object_status(pool_names=[poolname])
            status = None
            for i in rawpmstatus:
                for x in i:
                    if x.member.address == ip_address:
                        status = get_value_constant(x.object_status.enabled_status, CONS_BIGIP_ENABLE)
            return status