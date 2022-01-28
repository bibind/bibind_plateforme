# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ASPerience SARL (<http://www.asperience.fr>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time, os, random, string
from openerp import pooler
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp import pooler, tools
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
import json
from lxml import etree
import paramiko
from paramiko import SSHClient
import ovh
import gandi_odoo
from gandi_odoo import base
from gandi_odoo.base import GandiModule

_logger = logging.getLogger("dedaluvia_cloudservice")





class cloud_service_type_service(osv.osv):
    _name ='cloud.service.type'

class cloud_service_domain_gandi (osv.osv):
    _name = 'cloud.service.domain_gandi'
    _inherit = 'cloud.service'
    _description = 'cloud.service.domain.gandi'




    def creation_gandi_domain(self, cr, uid, ids, context):
        
        gandi = GandiModule()
        domain_spec = {
     'owner': 'AH4730-GANDI',
     'admin': 'AH4730-GANDI',
     'bill': 'AH4730-GANDI',
     'tech': 'AH4730-GANDI',
     'nameservers': ['a.dns.gandi-ote.net', 'b.dns.gandi-ote.net',
                     'c.dns.gandi-ote.net'],
     'duration': 1}
        create = gandi.safe_call('domain.create', domain, )


    #gestion des zones dns
    
    def getFournisseurZoneDnsrecordId(self, cr, uid, ids, context):
            # create a client using configuration
            zonerecords ={}
            client = ovh.Client(endpoint='ovh-eu')
            
            #validation = client.request_consumerkey(access_rules)
            for domain in self.browse( cr, uid, ids, context):
                zone = domain.domain

            zone = '/domain/zone/'+zone+'/record'
            zonerecords = client.get(zone)
       
            return zonerecords
        
        
    def getFournisseurLineZoneDnsrecordById(self, cr, uid, ids, record, context=None):
            # create a client using configuration
            linerecordid ={}
            client = ovh.Client(endpoint='ovh-eu')
            # Request RO, /me API access
            access_rules = [
                           {'method': 'GET', 'path': '/*'},
                            {'method': 'POST', 'path': '/*'},
                             {'method': 'PUT', 'path': '/*'},
                              {'method': 'DELETE', 'path': '/*'},
                          
                            ]
            # Request token
            #validation = client.request_consumerkey(access_rules)
            for domain in self.browse( cr, uid, ids, context=None):
                zone = domain.domain

            zone = '/domain/zone/%s/record/%s' %(zone,record)
            linerecordid = client.get(zone)
                   
            return linerecordid
        
        
        
    def getLineZonednsByRecords(self, cr, uid, ids, context):
        
        Records = self.getFournisseurZoneDnsrecordId(cr, uid, ids, context)
        _logger.info('recordes id  %s' % (Records))
        lines ={}
        for record in Records:
             try:
                 _logger.info('record in loop %s' % (record))
                 lines[record] = self.getFournisseurLineZoneDnsrecordById( cr, uid, ids, record, context)
             except IOError:
                 lines[record]=record
        
        return lines
    
    
    
    def _getValueZoneDnsByline(self, cr, uid, ids, line, vale, context):
        
        value ={}
        for this in self.browse(cr, uid, ids, context):
                 value['service_domain_id']=this.id
                 
        value['zone_dns_subdomain']=vale['subDomain']
        value['zone_dns_ovh_id']=vale['id']
        value['zone_dns_ttl']=vale['ttl']
        value['zone_dns_type']=vale['fieldType']
        value['zone_dns_cible']=vale['target']
        value['zone_dns_zone']=vale['zone']
        return value
    
            
        
           
    def loadRecordDomainZoneDns(self,cr, uid, ids, context):
        
        lines = self.getLineZonednsByRecords( cr, uid, ids, context)
        SdDns = self.pool.get('cloud.service.domain.zonedns')
        val ={}
        linezid={}
        for zoneid in lines:
            _logger.info('zoneid   %s' % (zoneid))
            vale = lines[zoneid]
            _logger.info('vale zoneid   %s' % (vale))
            value =self._getValueZoneDnsByline(cr, uid, ids,zoneid,vale, context)
            linezid[zoneid]= SdDns.create(cr, SUPERUSER_ID, value, context=context)
              
        return linezid
   
   #supression de toutes les linge zone dns
   
   
    def SupprimerforUpdateLineDnsZone(self, cr, uid, ids, context):
        
         ZoneDnsLine = self.pool.get('cloud.service.domain.gandi.zonedns')
         value ={}
         for this in self.browse(cr, uid, ids, context):
                 value['service_domain_id']=this.id
         
         ZoneDnsLineIds = ZoneDnsLine.search(cr, uid,[('service_domain_id','=', value['service_domain_id'])], context=None )
         _logger.info('zoneid   %s' % (ZoneDnsLineIds))
         for zoneDnsLineid in ZoneDnsLine.browse(cr, uid,ZoneDnsLineIds, context ):
             _logger.info(' zonedns id   %s' % (zoneDnsLineid.id))
             _logger.info('zonedns  %s' % (zoneDnsLineid))
             ZoneDnsLine.unlink(cr, uid,zoneDnsLineid.id, context)
             
         return True
    
    #gestion des serveur dns
    
    
    def getFournisseurServeurDnsrecordId(self, cr, uid, ids, context):
            # create a client using configuration
            servernamerecords ={}
            
            #validation = client.request_consumerkey(access_rules)
            for domain in self.browse( cr, uid, ids, context):
                zone = domain.domain

            zone = '/domain/'+zone+'/nameServer'
            servernamerecords = client.get(zone)
       
            return servernamerecords
        
        
    def getFournisseurLineServeurDnsrecordById(self, cr, uid, ids, record, context=None):
            # create a client using configuration
            linerecordid ={}
            client = ovh.Client(endpoint='ovh-eu')
            # Request RO, /me API access
            access_rules = [
                           {'method': 'GET', 'path': '/*'},
                            {'method': 'POST', 'path': '/*'},
                             {'method': 'PUT', 'path': '/*'},
                              {'method': 'DELETE', 'path': '/*'},
                          
                            ]
            # Request token
            #validation = client.request_consumerkey(access_rules)
            for domain in self.browse( cr, uid, ids, context=None):
                zone = domain.domain

            zone = '/domain/%s/nameServer/%s' %(zone,record)
            linerecordid = client.get(zone)
                   
            return linerecordid
    
    def getLineServeurdnsByRecords(self, cr, uid, ids, context):
        
        Records = self.getFournisseurServeurDnsrecordId(cr, uid, ids, context)
        _logger.info('recordes id  %s' % (Records))
        lines ={}
        for record in Records:
             try:
                 _logger.info('record in loop %s' % (record))
                 lines[record] = self.getFournisseurLineServeurDnsrecordById( cr, uid, ids, record, context)
             except IOError:
                 lines[record]=record
        
        return lines
    
    def _getValueServerDnsByline(self, cr, uid, ids, line, vale, context):
        
        value ={}
        for this in self.browse(cr, uid, ids, context):
                 value['service_domain_id']=this.id
                 
        value['serverdns_serveurdns']=vale['host']
        value['serverdns_ip']=vale['ip']
        value['serverdns_status']=vale['isUsed']
        
        value['serverdns_apiovh_id']=vale['id']
        value['serverdns_todel']=vale['toDelete']
       
        return value
    
    def loadRecordDomainServeurDns(self,cr, uid, ids, context):
        
        lines = self.getLineServeurdnsByRecords( cr, uid, ids, context)
        SdDns = self.pool.get('cloud.service.domain.gandi.dnsserver')
        val ={}
        linezid={}
        for zoneid in lines:
            _logger.info('zoneid   %s' % (zoneid))
            vale = lines[zoneid]
            _logger.info('vale zoneid   %s' % (vale))
            value =self._getValueServerDnsByline(cr, uid, ids,zoneid,vale, context)
            linezid[zoneid]= SdDns.create(cr, SUPERUSER_ID, value, context=context)
              
        return linezid
    
    #gestion Date d'expiration du nom de domain Che le fournisseur
    def loadExpiredate(self, cr, uid, ids, context):
            client = ovh.Client(endpoint='ovh-eu')
            
            #validation = client.request_consumerkey(access_rules)
            for domain in self.browse( cr, uid, ids, context=None):
                zone = domain.domain

            zone = '/domain/%s/serviceInfos' %(zone)
            linerecordid = client.get(zone)
            _logger.info('vale zoneid   %s' % (linerecordid))
            self.write(cr, uid, ids, {'expire_date': linerecordid['expiration']}, context=context)
              
            return linerecordid
    
    
    #domain propriété ovh
    def loadProprieteDomain(self, cr, uid, ids, context):
            client = ovh.Client(endpoint='ovh-eu')
            
            for domain in self.browse( cr, uid, ids, context=None):
                zone = domain.domain

            zone = '/domain/%s' %(zone)
            linerecordid = client.get(zone)
            _logger.info('vale zoneid   %s' % (linerecordid))
            
            self.write(cr, uid, ids, {'description': linerecordid}, context=context)
              
            return True
    
    
    
    
    
    
    #gestion des bouton d'action
    
    
    def button_load_records_Zonedns(self, cr, uid, ids, context):
              lines = self.loadRecordDomainZoneDns( cr, uid, ids, context)
              return True
    
    def button_load_records_serveurdns(self, cr, uid, ids, context):
              lines = self.loadRecordDomainServeurDns( cr, uid, ids, context)
              return True
          
    def button_load_domain_name(self, cr, uid, ids, context):
            value ={}
            for this in self.browse(cr, uid, ids, context):
                 value['name']=this.domain
            self.write(cr, uid, ids, {'name': value['name']}, context=context)
            return True 
    
    def button_load_expiredate(self, cr, uid, ids, context):
              self.loadExpiredate( cr, uid, ids, context)
              return True 
        

    def checkDomainFournisseur(self, cr, uid, ids, context):
            for this in self.browse(cr, uid, ids, context):
                 _logger.info('this id  %s' % (this.id))
            a =GandiModule()
             #r = a.safe_call('catalog.list',product_spec)
            r = a.safe_call('domain.info', ['terres-ile-chauvet.fr'])

            var = self.getLineAttacheDomainByRecords(cr, uid, ids, context)
            self.write(cr, uid, ids,  {'description':r}, context=context)
       
            
            return True

    def _getGestionDnsActivation(self, cr, uid, ids, fieldnames, args, context=None):
        
        result = {}
        for record in  self.browse(cr, uid, ids, context=context):
          result[record.id] = {
                record.id : 'Qui gere votre zone DNS',
            }
        return result

    _columns = {
        'domain' :fields.char('Nom de domain', size=256, required=True),
        
        'gestion_dns_activation': fields.function(_getGestionDnsActivation, type='text', string='Gestion DNS',
        help="Service permettant de traduire votre nom de domain en adresse ip , ou la gestion de vos emails."),
       
        'dnssec': fields.boolean(readonly=True, default=False, copy=False,
        help="Protection de la zone DNS du domain par authentifiaction."),
       
       'service_domain_zone_ids':fields.one2many('cloud.service.domain.zonedns', 'service_domain_id',"Zone DNS Lines"),   
       'service_domain_serveurdns_ids':fields.one2many('cloud.service.domain.dnsserver', 'service_domain_id',"Serveur DNS line")      
      
                 }
    _defaults = {
    }
    _order = 'id'
    
cloud_service_domain()
    
class cloud_service_domain_gandi_zonedns(osv.osv):
    _name = 'cloud.service.domain.gandi.zonedns'
    _description = 'cloud.service.domain.gandi.zonedns'
   
   
   
    _columns = {
        'zone_dns_subdomain':fields.char('Sous Domain', size=256),
        'zone_dns_ttl':fields.integer('TTL', default=10, required=True),
        'zone_dns_type':fields.selection([
            ('A','A'),
            ('AAAA','AAAA'),
            ('CNAME','CNAME'),
            ('NS','NS'),
            ('TXT','TXT'),
            ('NAPTR','NAPTR'),
            ('SRV','SRV'),
            ('LOC','LOC'),
            ('SSHFP','SSHFP'),
            ('MX','MX'),
            ('SPF','SPF'),
            ('DKIM','DKIM'),
        ],'Type de champs', size=256, required=True),
        
        
        
        'zone_dns_zone':fields.char('zone', size=256, required=True),
        'zone_dns_cible':fields.char('target', size=256, required=True),
        'zone_dns_ovh_id':fields.integer('ovh id', default=20, required=True),
       
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", required=True),
            
               } 
    _defaults = {
    }
    _order = 'id'
    
    
    
    def _getValueZoneDns(self, cr, uid,  vale, context):
        
        value ={}
        for this in self.browse(cr, uid, ids, context):
                 value['service_domain_id']=this.id
                 
        value['zone_dns_subdomain']=vale['subDomain']
        value['zone_dns_ovh_id']=vale['id']
        value['zone_dns_ttl']=vale['ttl']
        value['zone_dns_type']=vale['fieldType']
        value['zone_dns_cible']=vale['target']
        value['zone_dns_zone']=vale['zone']
        return value
    
    def GetRecordFournisseurZoneDnsById(self, cr, uid, ids, context):
            client = ovh.Client(endpoint='ovh-eu')
            # Request RO, /me API access
            access_rules = [
                           {'method': 'GET', 'path': '/*'},
                            {'method': 'POST', 'path': '/*'},
                             {'method': 'PUT', 'path': '/*'},
                              {'method': 'DELETE', 'path': '/*'},
                          
                            ]
            for domain in self.browse( cr, uid, ids, context=None):
                zone = domain.service_domain_id.name
                record =domain.zone_dns_ovh_id

            zone = '/domain/zone/%s/record/%s' %(zone,record)
            linerecordid = client.get(zone)
            return linerecordid
        
    def PutRecordFournisseurZoneDnsById(self, cr, uid, ids, context):
            client = ovh.Client(endpoint='ovh-eu')
            # Request RO, /me API access
            
            content ={}
            for zondns in self.browse( cr, uid, ids, context=None):
                zone = zondns.service_domain_id.name
                record =long(zondns.zone_dns_ovh_id)
               
                content['ttl']=zondns.zone_dns_ttl
                content['target']=zondns.zone_dns_cible
                content['subDomain']=zondns.zone_dns_subdomain
                content['fieldType']=zondns.zone_dns_type
            
            
            _logger.info('put zone %s' % (content))
            zone = '/domain/zone/%s/record/%s' %(zone,record)
            linerecordid = client.put(zone, **content)
            _logger.info('ovh return %s' % (linerecordid))
            return linerecordid

    def PostRecordFournisseurZoneDnsById(self, cr, uid, value, context):
            client = ovh.Client(endpoint='ovh-eu')
            # Request RO, /me API access
            access_rules = [
                           {'method': 'GET', 'path': '/*'},
                            {'method': 'POST', 'path': '/*'},
                             {'method': 'PUT', 'path': '/*'},
                              {'method': 'DELETE', 'path': '/*'},
                          
                            ]
            mondomain = self.pool.get('cloud.service.domain')
            mondomainid = mondomain.browse(cr, uid, value['service_domain_id'], context)
            content ={}
            content['subDomain']=value['zone_dns_subdomain']
            content['ttl']=value['zone_dns_ttl']
            content['target']=value['zone_dns_cible']
            content['fieldType']=value['zone_dns_type']
            
            zone = mondomainid.name
            _logger.info('put zone %s' % (content))

            zone = '/domain/zone/%s/record/' %(zone)
            _logger.info('put zone %s' % (zone))
            vale = client.post(zone,**content)
            
            
            values = {}
            values['service_domain_id']= value['service_domain_id']
            values['zone_dns_subdomain']=vale['subDomain']
            values['zone_dns_subdomain']=vale['subDomain']
            values['zone_dns_ovh_id']=vale['id']
            values['zone_dns_ttl']=vale['ttl']
            values['zone_dns_type']=vale['fieldType']
            values['zone_dns_cible']=vale['target']
            values['zone_dns_zone']=vale['zone']
            _logger.info('ovh return %s' % (values))
            
            return values
            
    
    def update_line_zone_dns(self, cr, uid, ids, context):
        res = self.PutRecordFournisseurZoneDnsById(cr, uid, ids, context)
        _logger.info('ovh return in button  %s' % (res))
        return True
    
    def update_line(self, cr, uid, ids, context):
        return True
    
    def create(self, cr, uid, vals, context):
        if(vals['zone_dns_ovh_id']==20):
            vals =self.PostRecordFournisseurZoneDnsById(cr, uid,  vals, context)
            res = super(cloud_service_domain_zonedns, self).create(cr, uid, vals, context=context)
        else:
            res = super(cloud_service_domain_zonedns, self).create(cr, uid, vals, context=context)
            _logger.info('vals cretat else  %s' % (vals))
        return res 
    
    
    def write(self, cr, uid, ids, vals, context=None):
         
         res = super(cloud_service_domain_zonedns,self).write(cr, uid, ids, vals, context)
         update = self.PutRecordFournisseurZoneDnsById(cr, uid, ids, context)
         _logger.info('vals write after  %s' % (res))
         return res
    
cloud_service_domain_zonedns()


class cloud_service_domain_gandi_dnsserver(osv.osv):

        _name = 'cloud.service.domain.gandi.dnsserver'
        _description = 'cloud.service.domain.gandi.dnsserver'
        
        
        
        def onchange_status(self, cr, uid, ids, part, context=None):
        
            return True
        
        
        _columns = {
         'serverdns_todel':fields.boolean('A supprimer', default=False, required=True),
        
        'serverdns_serveurdns':fields.char('Serveur DNS', size=256, required=True),
        'serverdns_status':fields.boolean('Status', default=False, required=True),
        'serverdns_apiovh_id':fields.integer('ovh id', default=20, required=True),
       'serverdns_ip':fields.integer('IP associé', default=256, required=True),
        
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", required=True),
            
               } 
        _defaults = {
                     }
        _order = 'id'
   
cloud_service_domain_dnsserver()

class cloud_service_hosting (osv.osv):
    _name = 'cloud.service.hosting'
    _inherit = 'cloud.service'
    _description = 'cloud.service.hosting'
    
    def getDomainByAttachedomainList(self, cr, uid, ids, context):
            # create a client using configuration
            zonerecords ={}
            client = ovh.Client(endpoint='ovh-eu')
            
            #validation = client.request_consumerkey(access_rules)
            for hosting in self.browse( cr, uid, ids, context):
                zone = hosting.name

            zone = '/hosting/web/%s/attachedDomain'%(zone)
            listDomain = client.get(zone)
       
            return listDomain
        
        
    def getAttachDomainRecordByDomain(self, cr, uid, ids, record, context=None):
            # create a client using configuration
            linerecordid ={}
            client = ovh.Client(endpoint='ovh-eu')
           
            #validation = client.request_consumerkey(access_rules)
            for hosting in self.browse( cr, uid, ids, context=None):
                zone = hosting.name
            _logger.info('recordes id  %s' % (zone))
            path = '/hosting/web/%s/attachedDomain/%s' %(zone,record)
            _logger.info('recordes id  %s' % (path ))
            linerecordid = client.get(path)
                   
            return linerecordid
    
    def getLineAttacheDomainByRecords(self, cr, uid, ids, context):
        
        Records = self.getDomainByAttachedomainList(cr, uid, ids, context)
        _logger.info('recordes id  %s' % (Records))
        lines ={}
        for record in Records:
             try:
                 _logger.info('record in loop %s' % (record))
                 lines[record] = self.getAttachDomainRecordByDomain( cr, uid, ids, record, context)
             except IOError:
                 lines[record]=record
        
        return lines
    
    def _getValueDomainByline(self, cr, uid, ids, line, vale, context):
        
        value ={}
        for this in self.browse(cr, uid, ids, context):
                 value['service_hosting_id']=this.id
         
        value['siteweb_domain']=vale['domain']
        value['siteweb_path']=vale['path']
        value['siteweb_cdn']=vale['cdn']
        
       
       
        return value
    
    def loadRecordDomainServeurDns(self,cr, uid, ids, context):
        
        lines = self.getLineAttacheDomainByRecords( cr, uid, ids, context)
        SdDns = self.pool.get('cloud.service.hosting.siteweb')
        val ={}
        linezid={}
        for zoneid in lines:
            _logger.info('zoneid   %s' % (zoneid))
            vale = lines[zoneid]
            _logger.info('vale zoneid   %s' % (vale))
            value =self._getValueDomainByline(cr, uid, ids,zoneid,vale, context)
            linezid[zoneid]= SdDns.create(cr, SUPERUSER_ID, value, context=context)
              
        return True
    
    
    
    def _getCountryByIp(self, cr, uid, ids, fieldnames, args, context=None):
        
        result = {}
        for record in  self.browse(cr, uid, ids, context=context):
          result[record.id] = {
                record.id : 'Qui gere votre zone DNS',
            }
        return result
    
    
    _columns = {
        
        'Espace_disque_quota':fields.char('Espace disque', size=256 ),
        'trafic_utilise':fields.char('Trafic', size=256 ),
        'trafic_quota':fields.char('Trafic', size=256 ),
        
        'Etat_du_service':fields.char('Etat du service', size=256 ),  
        'Offre':fields.char('Offre', size=256 ),
        'cluster_ipv4':fields.char('Adresse IPV4', size=256 ),
        'cluster_ovh':fields.char('Nom du Cluster', size=256),
        'certificat_ssl':fields.boolean('Certificat SSL', default=False ),
        'option_cdn':fields.boolean('Option CDN', default=False),
        'site_web':fields.char('Site web', size=256),
        'base_donne':fields.char('Base de donnée', size=256 ),
        'Espace_disque_utilise':fields.char('Name', size=256 ),
        'filer':fields.char('Filer', size=256 ), 
        'serveur_ftp':fields.char('serveur Ftp', size=256 ), 
        'login_ftp_principal':fields.char('Login ftp principal', size=256), 
        'log_text':fields.text('Log'),
        'path_home':fields.char('Home directory', size=256),
        'boostoffer':fields.char('boostOffer', size=256),
        'hostingipv6':fields.char('hostingipv6', size=256),
        'resourcetype':fields.char('ResourceType', size=256),
        'systemeos':fields.char('Systeme OS', size=256),
        'clusteripv6':fields.char('Cluster IPV6', size=256),
        
        
        
        'service_hosting_countryip_ids':fields.one2many('cloud.service.hosting.countryip', 'service_hosting_id',"IP des pays"),   
        
        'availableboostoffer':fields.one2many('cloud.service.hosting.availableboostoffer', 'service_hosting_id',"Boost Offer"),   
        'service_hosting_site_web_ids':fields.one2many('cloud.service.hosting.siteweb', 'service_hosting_id',"Zone DNS Lines"),   
        'service_hosting_bdd_ids':fields.one2many('cloud.service.hosting.sql', 'service_hosting_id',"Base de donnée line") ,     
        'service_hosting_ftp_ids':fields.one2many('cloud.service.hosting.ftp', 'service_hosting_id',"compte FTP") ,     
      
        
                }
    def checkPlatforme(self, cr, uid, ids, context):
            for this in self.browse(cr, uid, ids, context):
                 _logger.info('this id  %s' % (this.id))
      
            value ={}
            client = ovh.Client(endpoint='ovh-eu')
            path =  '/hosting/web/asagimbert.com' 
            content = client.get(path)
            
            value['name']=content['serviceName']
            value['Espace_disque_quota']=content['quotaSize']
            value['trafic_utilise']=content['trafficQuotaUsed']
            value['trafic_quota']=content['trafficQuotaSize']
            value['Etat_du_service']=content['state']
            value['Offre']=content['offer']
            value['cluster_ipv4']=content['clusterIp']
            value['cluster_ovh']=content['cluster']
            value['certificat_ssl']=content['hasHostedSsl']
            value['option_cdn']=content['hasCdn']
            
            
            value['Espace_disque_utilise']=content['quotaUsed']
            value['filer']=content['filer']
            value['serveur_ftp']=content['hostingIp']
            value['login_ftp_principal']=content['primaryLogin']
            value['log_text']=content['primaryLogin']
            #value['service_hosting_countryip_ids']=content['countriesIp']
           
            value['path_home']=content['home']
            value['boostoffer']=content['boostOffer']
            value['hostingipv6']=content['hostingIpv6']
            #value['availableboostoffer']=content['availableBoostOffer']
            value['resourcetype']=content['resourceType']
            value['systemeos']=content['operatingSystem']
            value['clusteripv6']=content['clusterIpv6']
        #'service_hosting_site_web_ids':   
        #'service_hosting_bdd_ids':     
        #'service_hosting_ftp_ids':     
            
            a = GandiModule()


            #r = a.safe_call('catalog.list',product_spec)
            r = a.safe_call('domain.available', ['terres-ile-chauvet.fr'])

            var = self.getLineAttacheDomainByRecords(cr, uid, ids, context)
            self.write(cr, uid, ids,  {'log_text':r}, context=context)
       
            return True


class cloud_service_hosting_countryip(osv.osv):    
    _name ='cloud.service.hosting.countryip'
    _description ='cloud.service.hosting.countryip'
    
    _columns = {
         'countryip_pays':fields.char('pays', required=True),
        
        'countryip_ip':fields.integer('ip',  required=True),
        
        'service_hosting_id':fields.many2one('cloud.service.hosting',"hosting", required=True),
            
               } 
    
    
class cloud_service_hosting_availableboostoffer(osv.osv):    
    _name ='cloud.service.hosting.availableboostoffer'
    _description ='cloud.service.hosting.availableboostoffer'
    
    _columns = {
         'offre':fields.char('type d\'offre', required=True),
        
        'price':fields.integer('price',  required=True),
        
        'service_hosting_id':fields.many2one('cloud.service.hosting',"hosting", required=True),
            
               } 

   
    
class cloud_service_hosting_siteweb(osv.osv):    
    _name ='cloud.service.hosting.siteweb'
    _description ='cloud.service.hosting.siteweb'
    
    _columns = {
        
        'siteweb_domain':fields.char('Serveur DNS', size=256, required=True),
        'siteweb_path':fields.char('Chemin du site', size=256, required=True),
        'siteweb_cdn':fields.char('CDN Etat', size=256, required=True),
        'service_hosting_id':fields.many2one('cloud.service.hosting',"hosting", required=True),
            
               } 






class cloud_service_hosting_sql(osv.osv):    
    _name ='cloud.service.hosting.sql'
    _description ='cloud.service.hosting.sql'
    
    _columns = {
        'sql_etat':fields.boolean('Activer ipv6', default=False, required=True),
        'sql_serveur':fields.char('Nom du serveur', size=256, required=True),
        'sql_taille':fields.char('Taille de la base', size=256, required=True),
        'sql_type':fields.char('Type de base de donnée', size=256, required=True),
        'sql_utilisateur':fields.char('ovh id', size=256, required=True),
        'service_hosting_id':fields.many2one('cloud.service.hosting',"hosting", required=True),
            
               } 






class cloud_service_hosting_ftp(osv.osv):    
    _name ='cloud.service.hosting.ftp'
    _description ='cloud.service.hosting.ftp'
    
    _columns = {
        
        'ftp_login':fields.char('Login', size=256, required=True),
        'ftp_repertoir':fields.char('Repertoire', size=256, required=True),
        'ftp_etat':fields.boolean('Etat', default=False, required=True),
        'ftp_ovh_id':fields.integer('id ovh api',  required=True),
        'service_hosting_id':fields.many2one('cloud.service.hosting',"hosting", required=True),
            
               } 








    
    
class cloud_service_serveur (osv.osv):
    _name = 'cloud.service.serveur'
    _inherit = 'cloud.service'
    _description = 'cloud.service.serveur'
    _columns = {
        'ip' :fields.char('', size=256, required=True),
        'type':fields.char('Name', size=256, required=True),
                
                }
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
