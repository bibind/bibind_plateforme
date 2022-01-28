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
#Domaine ovh api 

# GET /domain List available services
# GET /domain/zone List available services
# GET /domain/zone/{zoneName} Get this object properties
# GET /domain/zone/{zoneName}/dnssec Get this object properties
# POST /domain/zone/{zoneName}/dnssec Enable Dnssec
# DELETE /domain/zone/{zoneName}/dnssec Disable Dnssec
# GET /domain/zone/{zoneName}/dynHost/login DynHost' logins
# POST /domain/zone/{zoneName}/dynHost/login Create a new DynHost login
# GET /domain/zone/{zoneName}/dynHost/login/{login} Get this object properties
# PUT /domain/zone/{zoneName}/dynHost/login/{login} Alter this object properties
# DELETE /domain/zone/{zoneName}/dynHost/login/{login} Delete a DynHost login
# POST /domain/zone/{zoneName}/dynHost/login/{login}/changePassword Change password of the DynHost login
# GET /domain/zone/{zoneName}/dynHost/record DynHost' records
# POST /domain/zone/{zoneName}/dynHost/record Create a new DynHost record
# GET /domain/zone/{zoneName}/dynHost/record/{id} Get this object properties
# PUT /domain/zone/{zoneName}/dynHost/record/{id} Alter this object properties
# DELETE /domain/zone/{zoneName}/dynHost/record/{id} Delete a DynHost record
# GET /domain/zone/{zoneName}/export Export zone
# POST /domain/zone/{zoneName}/import Beta Import zone
# GET /domain/zone/{zoneName}/record Records of the zone
# POST /domain/zone/{zoneName}/record Create a new resource record
# GET /domain/zone/{zoneName}/record/{id} Get this object properties
# PUT /domain/zone/{zoneName}/record/{id} Alter this object properties
# DELETE /domain/zone/{zoneName}/record/{id} Delete a resource record
# GET /domain/zone/{zoneName}/redirection Redirections
# POST /domain/zone/{zoneName}/redirection Create a new redirection
# GET /domain/zone/{zoneName}/redirection/{id} Get this object properties
# PUT /domain/zone/{zoneName}/redirection/{id} Alter this object properties
# DELETE /domain/zone/{zoneName}/redirection/{id} Delete a redirection
# POST /domain/zone/{zoneName}/refresh Refresh zone
# GET /domain/zone/{zoneName}/serviceInfos Beta Get this object properties
# PUT /domain/zone/{zoneName}/serviceInfos Beta Alter this object properties
# GET /domain/zone/{zoneName}/soa Get this object properties
# PUT /domain/zone/{zoneName}/soa Alter this object properties
# GET /domain/zone/{zoneName}/task Domain pending tasks
# GET /domain/zone/{zoneName}/task/{id} Get this object properties
# GET /domain/{serviceName} Get this object properties
# PUT /domain/{serviceName} Alter this object properties
# GET /domain/{serviceName}/authInfo Return authInfo code if the domain is unlocked
# GET /domain/{serviceName}/nameServer List of current name servers
# POST /domain/{serviceName}/nameServer Add new name server
# GET /domain/{serviceName}/nameServer/{id} Get this object properties
# DELETE /domain/{serviceName}/nameServer/{id} Delete a name server
# GET /domain/{serviceName}/owo List of whois obfuscators
# POST /domain/{serviceName}/owo Add whois obfuscators
# GET /domain/{serviceName}/owo/{field} Get this object properties
# DELETE /domain/{serviceName}/owo/{field} Delete a whois obfuscator
# GET /domain/{serviceName}/serviceInfos Beta Get this object properties
# PUT /domain/{serviceName}/serviceInfos Beta Alter this object properties
# GET /domain/{serviceName}/task Domain pending tasks
# GET /domain/{serviceName}/task/{id} Get this object properties
############################################################################







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
import re
from lxml import etree
import paramiko
from paramiko import SSHClient
import ovh
import gandi_odoo
from gandi_odoo import base
from gandi_odoo.base import GandiModule
from socket import getaddrinfo

_logger = logging.getLogger("dedaluvia_cloudservice")


def password():
    length = 8
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))

class cloud_service (osv.osv):
    _name = 'cloud.service'
    _description = 'cloud.service'
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        
        return True
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)


    _columns = {
        'name':fields.char('Name', size=128 ),
        'description':fields.text('Description'),
        'write_date': fields.datetime(
            'Last Modified on',
            select=True, readonly=True,
        ),
        'create_date': fields.datetime(
            'Created on',
            select=True, readonly=True,
        ),
       'number_of_days': fields.integer('Quote Duration', help='Number of days for the validaty date computation of the service'),
        'expire_date': fields.datetime('Date d\'expiration',
            help='This is the date where the service as expired.'),
        
        'alert_date': fields.datetime('Alert Date',
            help="This is the date where le the customer would be alerted by the site ."),
    
        'partner_id' :fields.many2one('res.partner', string='Partenaire', required=True),
        'fournisseur_id' :fields.many2one('res.partner','Supplier',  required=True),
      
    }
    _defaults = {
    }
    _order = 'id'
    
cloud_service()

class cloud_service_domain (osv.osv):
    _name = 'cloud.service.domain'
    _inherit = 'cloud.service'
    _description = 'cloud.service.domain'




    #domain list 
    def getListDomain(self):
        client = ovh.Client(endpoint='ovh-eu')
        
        return True

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
                 
        value['ovh_subdomain']=vale['subDomain']
        value['ovh_id']=vale['id']
        value['ovh_ttl']=vale['ttl']
        value['ovh_type']=vale['fieldType']
        value['ovh_cible']=vale['target']
        value['ovh_zone']=vale['zone']
        return value
    
            
        
           
    def loadRecordDomainZoneDns(self,cr, uid, ids, context):
        
        lines = self.getLineZonednsByRecords( cr, uid, ids, context)
        SdDns = self.pool.get('cloud.service.domain.zone.')
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
        
         ZoneDnsLine = self.pool.get('cloud.service.domain.zonedns')
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
            client = ovh.Client(endpoint='ovh-eu')
           
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
            value['ovh_host']=vale['host']
            value['ovh_ip']=vale['ip']
            value['ovh_isUsed']=vale['isUsed']
            value['ovh_id']=vale['id']
            value['ovh_todel']=vale['toDelete']
       
        return value
    
    def loadRecordDomainServeurDns(self,cr, uid, ids, context):
        
        lines = self.getLineServeurdnsByRecords( cr, uid, ids, context)
        SdDns = self.pool.get('cloud.service.domain.nameserver')
        val ={}
        linezid={}
        for zoneid in lines:
            vale = lines[zoneid]
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
            self.write(cr, uid, ids, {'ovh_expire_date': linerecordid['expiration']}, context=context)
              
            return linerecordid
    
    
    def is_register(self,cr, uid, ids, context):
        client = ovh.Client(endpoint='ovh-eu')
            
        for domain in self.browse( cr, uid, ids, context=None):
                zone = domain.domain

        path = '/domain/%s' %(zone)
        register = client.get(path)
        if register['domain']== zone:
            return True
        else:
            return False
        
        
    def valid_register_domain(self,cr, uid, ids, context):
        if self.is_register(cr, uid, ids, context):
                self.loadRegisterDomainPropriete(cr, uid, ids, context)
                self.write(cr, uid, ids, {'state': 'done'}, context=context)
         
    
    def loadRegisterDomainPropriete(self,cr,uid,ids,context):
        self.loadRecordDomainZoneDns(cr, uid, ids, context)
        self.loadRecordDomainServeurDns(cr, uid, ids, context)
        self.loadExpiredate(cr, uid, ids, context)

    #gestion des bouton d'action
    
    def button_verif_is_domain_isregister(self,cr,uid,ids,context):
            self.valid_register_domain(cr, uid, ids, context)
        
    
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
      
      
            client = ovh.Client(endpoint='ovh-eu')
           
            #validation = client.request_consumerkey(access_rules)
           # Request token
            validation = client.request_consumerkey(access_rules)
             
             #text = "Please visit %s to authenticate" % validation['validationUrl']
                   # Print nice welcome message
            text2 = "Please visit %s to authenticate" % (validation['consumerKey'])
            #text3 = "Btw, your 'consumerKey' is '%s'" % validation['consumerKey']
            
            self.write(cr, uid, ids, {'description': text2}, context=context)
       
            return True

    def _getGestionDnsActivation(self, cr, uid, ids, fieldnames, args, context=None):
        
        result = {}
        for record in  self.browse(cr, uid, ids, context=context):
          result[record.id] = {
                record.id : 'Qui gere votre zone DNS',
            }
        return result
    
    def get_list_available_domain(self, cr, uid, ids, context=None):
        """ on est oblige d'acheter une plateforme ovh pour un domain  """
       
        
    
    def verifieDisponibilitedomain(self, cr, uid, ids, context=None):
        """ se créer à ovh pour voir la disponibilité de command  """
        client = ovh.Client(endpoint='ovh-eu')
        for this in self.browse(cr, uid, ids, context):
                 domain=this.domain
        dispo = soapi_ovh()
        result = dispo.domain_check(domain)
        if result:
            self.write(cr, uid, ids, {'state': 'valide'}, context=context)
      
    def Buydomain(self, cr, uid, ids, context=None):
        """ se créer à ovh pour voir la disponibilité de command  """
        
        client = ovh.Client(endpoint='ovh-eu')
        for this in self.browse(cr, uid, ids, context):
                 domain=this.domain
        dispo = soapi_ovh()
        result = dispo.domain_create(domain)
        if result==None:
            self.write(cr, uid, ids, {'state': 'attente_register'}, context=context)
 
    
    
    def verifDispo(self, cr, uid, ids, context=None):
        """ se créer à ovh pour voir la disponibilité de command  """
        client = ovh.Client(endpoint='ovh-eu')
         
        #for domain in self.browse( cr, uid, ids, context=None):
         #       zone = domain.domain

            #zone = 'order/domain/%s' %(zone)
        DOMAIN = "dedaloyat.com"
        duration = "12"
        OFFER = "PERFORMANCE_1"
        #o = "contact@example.com"
        zone = '/order/hosting/web/new/%s' %duration
        linerecordid = client.get(zone, domain=DOMAIN, offer=OFFER)
        #zone ='/order/hosting/web/new/'
        #linerecordid = client.get(zone)
        
        _logger.info('vale zoneid   %s' % (linerecordid))
        self.write(cr, uid, ids, {'description': linerecordid}, context=context)
       
        
        return True
    
    
    def active_domain(self, cr, uid, ids, context=None):
        
        return True
    
    
    def _check_domain(self, cr, uid, ids, context=None):
        for val in self.read(cr, uid, ids, ['domain'], context=context):
            if val['domain']:
                string = val['domain']
                regex = r'^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}$'
                if re.match(regex, string) is not None:
                        return True
                else:
                        return False

    _columns = {
        'domain' :fields.char('Nom de domain', size=256, required=True),
       
        'state': fields.selection([
            ('draft', 'Domain brouillon'),
            ('valide', 'Domain disponible'),
            ('attente_register', 'Domain en attente du register'),
            
            ('done', 'Domain enregistré'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the domain.\
              .", select=True),
        
       #ovh champ objet zonedns  /domain/zone 
       'service_domain_zone_ids':fields.one2many('cloud.service.domain.zone.record','service_domain_id', "Zone dns"),     
      
       #ovh champ objet gestion serveurdns /domain/{servicename}/nameserver
       'service_domain_nameserver_ids':fields.one2many('cloud.service.domain.nameserver', 'service_domain_id',"Serveur nameline"),     
       
       #ovh champ objet DNSSEC /domain/zone/{zonename}/dnsec
       'ovh_dnssec': fields.selection([
            ('disableInProgress', 'en cours de désactivation'),
            ('disabled', 'Désactivé'),
            ('enableInProgress', 'En cour d\'activation'),
            
            ('enabled', 'Activé'),
            ], 'DNSSEC Status', readonly=True, copy=False, help="Protéger votre domain contre cache poisoning.", select=True),
     
      
       #ovh champ objet dynHosting login  /domain/zone/{zoneName}/dynHost/login
       #'service_domain_zone_dynhosting_login_ids':fields.one2many('cloud.service.domain.zone.dynhost.login', 'service_domain_id',"Login dynHost"),     
     
       
       #ovh champ objet dynHosting  /domain/zone/{zoneName}/dynHost/record
       #'service_domain_zone_dynhosting_ids':fields.one2many('cloud.service.domain.zone.dynhost', 'service_domain_id',"Entree DynHost"),     
     
     
       #ovh champ objet /domain/zone/{zoneName}/redirection
       'service_domain_zone_redirection_ids':fields.one2many('cloud.service.domain.zone.redirection', 'service_domain_id',"Redirection"),     
     
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
     
     
       #ovh champ ovh task internal mane /domain/{serviceName}/task / {id}
       'service_domain_task_ids':fields.many2one('cloud.service.domain.task', 'service_domain_id',"Task"),     
     
     
       #ovh champ owo internal /domain/{serviceName}/owo/{field}
       'service_domain_owo_id':fields.many2one('cloud.service.domain.owo', 'service_domain_id',"Masquage du WHOIS", ondelete="cascade"),     
     
      #ovh champ email internal /domain/{serviceName}/owo/{field}
       'service_domain_email_id':fields.many2one('cloud.service.domain.email', 'service_domain_id',"Email", ondelete="cascade"),     
     
       
       #champs ovh domain/{servicename}
       'ovh_last_update' : fields.datetime('Dernière mis à jour sur ovh',
            help='This is the date where the service as update in the register ovh.'),
        
        'ovh_nameServerType':fields.char('Seveur qui gere les dns', size=256,
                                     help='Service permettant de traduire votre nom de domain en adresse ip , ou la gestion de vos emails.'),
        
        'ovh_offer':fields.char('Offre ovh domain', size=256),
        
        'ovh_transferLockStatus':fields.char('bloquage des transfert', size=256),
        
        'ovh_owoSupported':fields.boolean('Masquage du WHOIS',readonly=True, default=False, copy=False,
                                       help='Base de donnée publiquement accessible contenant les information personnelles de votre domain'),
       
        #ovh champ /domain/{servicename}/serviceInfo
          
          #ovh status
          'ovh_status':fields.selection([
                                        ("expired","expired"),
                                        ("inCreation","inCreation"),
                                        ("ok","ok"),
                                        ("unPaid","unPaid")
                                        ],'State', help=""),
            #date 
            'ovh_engagedUpTo':fields.datetime(),
            #All the possible renew period of your service in month type long
            'ovh_possibleRenewPeriod':fields.integer('', help="All the possible renew period of your service in month"),
            #Objet ovh_nichandle billing contact billing
            'ovh_contactBilling':fields.char('Ovh contact billing'),
            #objet renew
            'ovh_renew':fields.many2one('cloud.service.type.renew', 'service_domain_id',"Email", ondelete="cascade"),
            #string
            'ovh_domain':fields.char('Domain'),
            #date
            'ovh_expiration': fields.datetime('Date d\'expiration chez Ovh',
            help='This is the date where the service as expired.'),
            #objet ovh_nichandle
            'ovh_contactTech':fields.char('Ovh contact Technique'),
            #objet ovh_nichandle
            'ovh_contactAdmin':fields.char('Ovh contact Admin'),
            #date
            'ovh_creation':fields.datetime('Date de création chez Ovh',
            help='date de création chez ovh.'),
                
                
            
        
                 }
    
    
    
            
    _defaults = {
                  'state': 'draft',
    }
    
    _constraints = [ (_check_domain, "Insérer un nom de domain valide", ['domain'])]




   
####################action sur le service domain avec création de task ovh####################

                #POST domain import zone /domain/zone/{zoneName}/import 
    def import_domain_zone(self,cr, uid, ids,value, context):
        
        return True
   
                #POST domain name server  /domain/{serviceName}/nameServer
    def create_domain_nameserver(self,cr, uid, ids,value, context):
        
        return True
   
############################################################################################




####################action sur le service domain sans taches ovh####################

                #POST domain refresh zone /domain/zone/{zoneName}/refresh 
    def refresh_domain_zone(self,cr, uid, ids,value, context):
        
        return True
   
                #GET authinfo pur domain unlocked  /domain/{serviceName}/authInfo
    def get_domain_authinfo(self,cr, uid, ids,value, context):
        
        return True
   
#########################################################################################
                
                
                
                
                #domain propriété ovh
    def loadProprieteDomain(self, cr, uid, ids, context):
            client = ovh.Client(endpoint='ovh-eu')
            
            for domain in self.browse( cr, uid, ids, context=None):
                servicename = domain.domain

            path = '/domain/%s' %(servicename)
            vale = client.get(path)
            value ={}
            value['gestion_dns_activation']=vale['nameServerType']
            value['ovh_dnssec']= False
            value['ovh_last_update']=vale['lastUpdate']
            value['ovh_offer']=vale['offer']
            value['ovh_owoSupported']=vale['owoSupported']
            
            value['ovh_transferLockStatus']=vale['isUsed']
            
            path2 = '/domain/%s/serviceInfo' %(servicename)
            vale2 = client.get(path)
           
            # sevice info ovh
            #"status domain select expired" "inCreation" "ok" "unPaid"
            value['ovh_status']=vale2['status']
            #date 
            value['ovh_engagedUpTo']= vale2['engagedUpTo']
            #All the possible renew period of your service in month type long
            value['ovh_possibleRenewPeriod']=vale2['possibleRenewPeriod']
            #Objet ovh_nichandle billing contact billing
            value['ovh_contactBilling']=vale2['contactBilling']
            #objet renew
            value['ovh_renew']=vale2['renew']
            #string
            value['ovh_domain']=vale2['domain']
            #date
            value['ovh_expiration']=vale2['expiration']
            #objet ovh_nichandle
            value['ovh_contactTech']= vale2['contactTech']
            #objet ovh_nichandle
            value['ovh_contactAdmin']=vale2['contactAdmin']
            #date
            value['ovh_creation']=vale2['creation']
          
            

            
            
            _logger.info('vale zoneid   %s' % (linerecordid))
            
            self.write(cr, uid, ids, {'description': linerecordid}, context=context)
              
            return True


   
    
cloud_service_domain()


class cloud_service_domain_zone(osv.osv):
    _name = 'cloud.service.domain.zone'
    _description = 'cloud.service.domain.zone'
   
   
   
    _columns = {
        'zone_name':fields.char('zone name', size=256, requere=True, help="La zone du nom de domain , généralement le nom de domain, "),
        'ovh_lastUpdate':fields.datetime('last update'),
        'ovh_hasDnsAnycast':fields.boolean('hasDnsAnycast', default=False, required=True),
        'ovh_nameServers':fields.char('Name serveur', size=256 ),
        'ovh_dnssecSupported':fields.char('DNSSEC supported', size=256, required=True),
        
        
        #ovh champ ovh task internal zone name /domain/zone/{zoneName}/task / {id}
       'service_domain_zone_task_ids':fields.one2many('cloud.service.domain.zone.task', 'service_domain_zone_id',"zone Task"),     
     
        #ovh lien avec un domain ovh
        #'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
        #ovh champ objet zone records  /domain/zone 
        'service_domain_zone_ids':fields.one2many('cloud.service.domain.zone.record', 'service_zone_id',"Serveur DNS line"),     
      
               } 
    _defaults = {
                 
    }
    _order = 'id'
    
    
class cloud_service_domain_zone_task(osv.osv):
     
      _name = 'cloud.service.domain.zone.task'
      _description = 'cloud.service.domain.zone.task'

      _columns = {
        'ovh_function':fields.char('Function of the task', size=256, required=True),
       
        'ovh_lastUpdate':fields.datetime('lastUpdate', required=True,
                                      help='Last update date of the task'),
         
        
        'ovh_comment':fields.char('comment', size=256, required=True,
                                      help='Comment about the task'),
        'ovh_status':fields.selection([
                            ("cancelled","cancelled"),
                            ("doing","doing"),
                            ("done","done"),
                            ("error","error"),
                            ( "todo","todo")
                            ], 'status', required=True,
                                  help='The serial number is used to indicate which copy of the zone file is the most current. When editing zone files, you must increment the serial number'),
       
       'ovh_todoDate':fields.datetime('Todo date of the task', size=256, required=True,
                                      help='Todo date of the task'),
        'ovh_doneDate':fields.datetime('doneDate', size=256, required=True,
                                  help='Done date of the task'),
       
       
        'ovh_id':fields.integer('ovh record id', default=20, required=True),
     
        'service_domain_zone_id':fields.many2one('cloud.service.domain.zone',"nom de la zone", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'
      


class cloud_service_domain_zone_record(osv.osv):
    _name = 'cloud.service.domain.zone.record'
    _description = 'cloud.service.domain.zone.record'
   
   
   
    _columns = {
        'ovh_subdomain':fields.char('Sous Domain', size=256),
        'ovh_ttl':fields.integer('TTL', default=10, required=True),
        'ovh_type':fields.selection([
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
        
        
        
        'ovh_zone':fields.char('zone', size=256, required=True),
        'ovh_cible':fields.char('target', size=256, required=True),
        'ovh_id':fields.integer('ovh id', default=20, required=True),
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
       
        'service_zone_id':fields.many2one('cloud.service.domain.zone',"Nom de la zone", ondelete='cascade', required=True,),
            
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
            mondomain = self.pool.get('cloud.service.domain')
            mondomainid = mondomain.browse(cr, uid, value['service_domain_id'], context)
            content ={}
            content['subDomain']=value['ovh_subdomain']
            content['ttl']=value['ovh_ttl']
            content['target']=value['ovh_cible']
            content['fieldType']=value['ovh_type']
            
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
        if(vals['ovh_id']==20):
            vals =self.PostRecordFournisseurZoneDnsById(cr, uid,  vals, context)
            res = super(cloud_service_domain_zone, self).create(cr, uid, vals, context=context)
        else:
            res = super(cloud_service_domain_zone, self).create(cr, uid, vals, context=context)
            _logger.info('vals cretat else  %s' % (vals))
        return res 
    
    
    def write(self, cr, uid, ids, vals, context=None):
         
         res = super(cloud_service_domain_zone,self).write(cr, uid, ids, vals, context)
         update = self.PutRecordFournisseurZoneDnsById(cr, uid, ids, context)
         _logger.info('vals write after  %s' % (res))
         return res
    
cloud_service_domain_zone()


class cloud_service_domain_nameserver(osv.osv):

        _name = 'cloud.service.domain.nameserver'
        _description = 'cloud.service.domain.nameserver'
        
        
        
        def onchange_status(self, cr, uid, ids, part, context=None):
        
            return True
        
        
        _columns = {
        'ovh_toDelete':fields.boolean('A supprimer', default=False, required=True),
        'ovh_host':fields.char('Serveur DNS', size=256, required=True),
        'ovh_isUsed':fields.boolean('Status', default=False, required=True),
        'ovh_id':fields.integer('ovh id', default=20, required=True),
        'ovh_ip':fields.integer('IP associé', default=256, required=True),
        
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
            
               } 
        _defaults = {
                     }
        _order = 'id'
   
cloud_service_domain_nameserver()


class cloud_service_domain_zone_dynhost_login(osv.osv):
#ovh champ objet dynHosting login  /domain/zone/{zoneName}/dynHost/login
       #'service_domain_dynhosting_login_ids':fields.one2many('cloud.service.domain.dynhost.login', 'service_domain_id',"Login dynHost"),     
      _name = 'cloud.service.domain.zone.dynhost.login'
      _description = 'cloud.service.domain.zone.dynhost.login'
      
      _columns = {
        'ovh_zone':fields.char('Zone', size=256, required=True),
        'ovh_subdomain':fields.char('subdomain', size=256, required=True),
        'ovh_loginsuffix':fields.char('suffixlogin', size=256, required=True),
        'password':fields.char('password', size=256, required=True),
        'id_ovh_record_login':fields.integer('ovh id login', default=20, required=True),
     
        'service_zone_id':fields.many2one('cloud.service.domain.zone',"Nom de domain", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'
      

class cloud_service_domain_zone_dynhost(osv.osv):   
       #ovh champ objet dynHosting  /domain/zone/{zoneName}/dynHost/record
       #'service_domain_dynhosting_ids':fields.one2many('cloud.service.domain.dynhost', 'service_domain_id',"Entree DynHost"),     
      _name = 'cloud.service.domain.zone.dynhost'
      _description = 'cloud.service.zone.domain.dynhost'
      
      _columns = {
        'ovh_ip':fields.char('ip dynHost', size=256, required=True),
       
        'ovh_zone':fields.char('Zone name dynHost', size=256, required=True),
        'ovh_subdomain':fields.char('Subdomain cible', size=256, required=True),
        'id_ovh_record':fields.integer('ovh record id', default=20, required=True),
     
        'service_domain_zone_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'
     
class cloud_service_domain_zone_redirection(osv.osv):
       #ovh champ objet /domain/zone/{zoneName}/redirection
       #'service_domain_redirection_ids':fields.one2many('cloud.service.domain.redirection', 'service_domain_id',"Redirection"),     
      _name = 'cloud.service.domain.zone.redirection'
      _description = 'cloud.service.domain.zone.redirection'
      
      _columns = {
        'ovh_keywords':fields.char('Keywords for invisible redirection', size=256, required=True),
        'ovh_target':fields.char('Target of the redirection', size=256, required=True),
        'ovh_zone':fields.char('Redirection zone', size=256, required=True),
            
        'ovh_subDomain':fields.char('Subdomain cible', size=256, required=True),
        'ovh_type':fields.selection(
                                    [('invisible','invisible'),
            ('visible','visible'),
            ('visiblePermanent','visiblePermanent'),
        ],'Type de redirection', size=256, required=True,
                                    help='Redirection type enum : visible -> Redirection by http code 302, visiblePermanent -> Redirection by http code 301, invisible -> Redirection by html frame'),
        
        'ovh_title':fields.char('Title for invisible redirection', size=256, required=True),
        'ovh_description':fields.char('Desciption for invisible redirection', size=256, required=True),
       
        'id_ovh_record':fields.integer('ovh record id', default=20, required=True),
      
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'
      
      
      
class cloud_service_domain_soa(osv.osv):
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       #'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
      _name = 'cloud.service.domain.soa'
      _description = 'cloud.service.domain.soa'

      _columns = {
        'ovh_email':fields.char('Email address of the DNS Administrator', size=256, required=True),
       
        'ovh_nxDomainTtl':fields.char('nxDomainTtl', size=256, required=True,
                                      help='Non-Existent Domain TTL, if the name server returns a negative response, the remote server should wait the number of seconds set in the nxDomainTtl field before trying again'),
        'ovh_refresh':fields.char('refresh', size=256, required=True,
                                  help='The refresh value determines the interval in seconds between successful zone transfers of the entire zone file from a nameserver to another.'),
        
        
        'ovh_ttl':fields.char('ttl', size=256, required=True,
                                      help='Time To Live in seconds'),
        'ovh_serial':fields.char('serial', size=256, required=True,
                                  help='The serial number is used to indicate which copy of the zone file is the most current. When editing zone files, you must increment the serial number'),
       
       'ovh_server':fields.char('server', size=256, required=True,
                                      help='Primary authoritative server'),
        'ovh_expire':fields.char('expire', size=256, required=True,
                                  help='When a zone transfer fails, a countdown clock begins. When the number of seconds set in the expire field elapses, the nameserver stops answering for that zone file'),
       
       
        'id_ovh_record':fields.integer('ovh record id', default=20, required=True),
     
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'

      
class cloud_service_domain_task(osv.osv):
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       #'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
      _name = 'cloud.service.domain.task'
      _description = 'cloud.service.domain.task'

      _columns = {
        'ovh_function':fields.char('Function of the task', size=256, required=True),
       
        'ovh_lastUpdate':fields.datetime('lastUpdate', required=True,
                                      help='Last update date of the task'),
         
        
        'ovh_comment':fields.char('comment', size=256, required=True,
                                      help='Comment about the task'),
        'ovh_status':fields.selection([
                            ("cancelled","cancelled"),
                            ("doing","doing"),
                            ("done","done"),
                            ("error","error"),
                            ( "todo", "todo")
                            ], 'status', size=256, required=True,
                                  help='The serial number is used to indicate which copy of the zone file is the most current. When editing zone files, you must increment the serial number'),
       
       'ovh_todoDate':fields.datetime('Todo date of the task', size=256, required=True,
                                      help='Todo date of the task'),
        'ovh_doneDate':fields.datetime('doneDate', size=256, required=True,
                                  help='Done date of the task'),
       
       
        'ovh_id':fields.integer('ovh record id', default=20, required=True),
     
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'
      
      
class cloud_service_domain_owo(osv.osv):
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       #'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
      _name = 'cloud.service.domain.owo'
      _description = 'cloud.service.domain.owo'

      _columns = {
        
        'ovh_field':fields.selection(
                                    [('adress','adress'),
            ('email','email'),
            ('phone','phone'),
        ],'Whois configuration', size=256, required=True,
                                    help='Whois obfuscable fields'),
        
        
        'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'


class cloud_service_domain_email(osv.osv):
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       #'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
      _name = 'cloud.service.domain.email'
      _description = 'cloud.service.domain.email'

      _columns = {

      'ovh_filerz':fields.boolean(),
      'ovh_domain':fields.char(),
      'ovh_creationDate':fields.char(),
      'ovh_status':fields.char(),
      'ovh_allowedAccountSize':fields.char(),
      
      
      'service_domain_id':fields.many2one('cloud.service.domain',"Nom de domain", ondelete='cascade', required=True),
            
               } 
      _defaults = {
                     }
      _order = 'id'
      
      

class cloud_service_domain_email_quota(osv.osv):    
    _name ='cloud.service.domain.email.quota'
    _description ='cloud.service.domain.email.quota'
    
    _columns = {
        
      'ovh_responder': fields.char(),
      'ovh_account':fields.char(),
      'ovh_mailingList':fields.char(),
      'ovh_redirection':fields.char(),
      'ovh_alias':fields.char(),

               } 


class cloud_service_domain_email_redirection(osv.osv):    
   #GET /email/domain/{domain}/redirection/{id} 
    _name ='cloud.service.domain.email.quota'
    _description ='cloud.service.domain.email.quota'
    
    _columns = {
        
         'ovh_to': fields.char(),
      'ovh_from':fields.char(),
      'ovh_id':fields.char(),
      

               } 


class cloud_service_domain_email_responder(osv.osv):    
    _name ='cloud.service.domain.email.quota'
    _description ='cloud.service.domain.email.quota'
    
    _columns = {
         'ovh_copy': fields.char(),
      'ovh_to':fields.char(),
      'ovh_copyTo':fields.char(),
      'ovh_account':fields.char(),
      'ovh_from':fields.char(),
            'ovh_content':fields.char(),
      
               } 


class cloud_service_domain_email_account(osv.osv):
     
     #GET /email/domain/{domain}/responder/{account} 
      _name = 'cloud.service.domain.email.account'
      _description = 'cloud.service.domain.email.account'

      _columns = {
        
      'ovh_isblocked':fields.boolean(),
      'ovh_domain':fields.char(),
      'ovh_description':fields.char(),
      'ovh_accountName':fields.char(),
      'ovh_size':fields.char(),
      
      
            
               } 
      _defaults = {
                     }
      _order = 'id'
      
      
class cloud_service_domain_email_account_filter(osv.osv):
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       #'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
      _name = 'cloud.service.domain.email.account.filter'
      _description = 'cloud.service.domain.email.account.filter'

      _columns = {
                
                
      'ovh_priority': fields.char(),
      'ovh_domain':fields.char(),
      'ovh_actionParam':fields.char(),
      'ovh_active':fields.char(),
      'ovh_name':fields.char(),
      'ovh_action':fields.char(),
       'ovh_pop':fields.char(),
        
            
               } 
      _defaults = {
                     }
      _order = 'id'
      

class cloud_service_domain_email_account_filter_rule(osv.osv):
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       #'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
      _name = 'cloud.service.domain.email.account.filter.rule'
      _description = 'cloud.service.domain.email.account.filter.rule'

      _columns = {
        
        
      'ovh_value': fields.char(),
      'ovh_operand':fields.char(),
      'ovh_id':fields.char(),
      'ovh_header':fields.char(),
      'ovh_name':fields.char(),
      'ovh_action':fields.char(),

             
               } 
      _defaults = {
                     }
      _order = 'id'
      
     
class cloud_service_domain_email_mailinglist(osv.osv):
     
      _name = 'cloud.service.domain.email.mailinglist'
      _description = 'cloud.service.domain.email.mailinglist'

      _columns = {
        
        
      'ovh_language': fields.char(),
      'ovh_options':fields.char(),
      'ovh_name':fields.char(),
      'ovh_ownerEmail':fields.char(),
      'ovh_replyTo':fields.char(),
      'ovh_id':fields.char(),
      'ovh_nbSubscribersUpdateDate':fields.char(),
      'ovh_nbSubscribers':fields.char(),
             
               } 
      _defaults = {
                     }
      _order = 'id'
      
class cloud_service_domain_email_mailinglist_name_moderateur(osv.osv):
      
      _name = 'cloud.service.domain.email.mailinglist.name.moderateur'
      _description = 'cloud.service.domain.email.mailinglist.name.moderateur'

      _columns = {
        
      'ovh_email': fields.char(),
      'ovh_domain':fields.char(),
      'ovh_mailinglist':fields.char(),      
      
             
               } 
      _defaults = {
                     }
      _order = 'id'
      

class cloud_service_domain_email_task_account(osv.osv):    
    _name ='cloud.service.domain.email.task.account'
    _description ='cloud.service.domain.email.task.account'
    
    _columns = {
        
      'ovh_domain':fields.char('Domain',  help="Function name"),
      'ovh_date':fields.datetime('Date', size=256, required=True, help="last update"),
       'ovh_name':fields.char('Name',  help="Function name"),
     
      
      'ovh_action':fields.selection([
                               ( "addAccount","addAccount"),
                                ("changeAccount","changeAccount"),
                                 ( "changePassword","changePassword"),
                                ("deleteAccount","deleteAccount"),
                                
                                ], 'Tasks status', size=256, required=True ,help="The type of the admin name"),
       
      'ovh_id':fields.integer('the id of the task',  help="the id of the task"),
        
        
      'ovh_startDate':fields.datetime('startdate',size=256, help="Task Creation date"),
      'ovh_doneDate':fields.datetime('donedate',size=256, help="Completion date"),
             
               } 


class cloud_service_domain_email_task_filter(osv.osv):    
    _name ='cloud.service.domain.email.task.filter'
    _description ='cloud.service.domain.email.task.filter'
    
    _columns = {
        
      'ovh_domain':fields.char('Domain',  help="Function name"),
      'ovh_date':fields.datetime('Date', size=256, required=True, help="last update"),
       'ovh_account':fields.char('account',  help="Function name"),
     
      
      'ovh_action':fields.selection([
                               ( "addAccount","addAccount"),
                                ("changeAccount","changeAccount"),
                                 ( "changePassword","changePassword"),
                                ("deleteAccount","deleteAccount"),
                                
                                ], 'Tasks status', size=256, required=True ,help="The type of the admin name"),
       
      'ovh_id':fields.integer('the id of the task',  help="the id of the task"),
        
        
      'ovh_startDate':fields.datetime('startdate',size=256, help="Task Creation date"),
      'ovh_doneDate':fields.datetime('donedate',size=256, help="Completion date"),
             
               } 


class cloud_service_domain_email_task_redirection(osv.osv):    
    _name ='cloud.service.domain.email.task.redirection'
    _description ='cloud.service.domain.email.task.redirection'
    
    _columns = {
        
      'ovh_function':fields.char('Function name',  help="Function name"),
      'ovh_lastUpdate':fields.datetime('last update', size=256, required=True, help="last update"),
      'ovh_status':fields.selection([
                               ( "cancelled","cancelled"),
                                ("doing","doing"),
                                 ( "done","done"),
                                ("error","error"),
                                 ( "init","init"),
                                ("todo","todo"),
                                ], 'Tasks status', size=256, required=True ,help="The type of the admin name"),
       
      'ovh_id':fields.integer('the id of the task',  help="the id of the task"),
        
        
      'ovh_startDate':fields.datetime('startdate',size=256, help="Task Creation date"),
      'ovh_doneDate':fields.datetime('donedate',size=256,  required=True, help="Completion date"),
                } 



class cloud_service_domain_email_task_responder(osv.osv):    
    _name ='cloud.service.domain.email.task.responder'
    _description ='cloud.service.domain.email.task.responder'
    
    _columns = {
        
      'ovh_function':fields.char('Function name',  help="Function name"),
      'ovh_lastUpdate':fields.datetime('last update', size=256, required=True, help="last update"),
      'ovh_status':fields.selection([
                               ( "cancelled","cancelled"),
                                ("doing","doing"),
                                 ( "done","done"),
                                ("error","error"),
                                 ( "init","init"),
                                ("todo","todo"),
                                ], 'Tasks status', size=256, required=True ,help="The type of the admin name"),
       
      'ovh_id':fields.integer('the id of the task',  help="the id of the task"),
        
        
      'ovh_startDate':fields.datetime('startdate',size=256, help="Task Creation date"),
      'ovh_doneDate':fields.datetime('donedate',size=256,  required=True, help="Completion date"),
             
               } 

class cloud_service_domain_email_task_mailinglist(osv.osv):    
    _name ='cloud.service.domain.email.task.mailinglist'
    _description ='cloud.service.domain.email.task.mailinglist'
    
    _columns = {
        
      'ovh_function':fields.char('Function name',  help="Function name"),
      'ovh_lastUpdate':fields.datetime('last update', size=256, required=True, help="last update"),
      'ovh_status':fields.selection([
                               ( "cancelled","cancelled"),
                                ("doing","doing"),
                                 ( "done","done"),
                                ("error","error"),
                                 ( "init","init"),
                                ("todo","todo"),
                                ], 'Tasks status', size=256, required=True ,help="The type of the admin name"),
       
      'ovh_id':fields.integer('the id of the task',  help="the id of the task"),
        
        
      'ovh_startDate':fields.datetime('startdate',size=256, help="Task Creation date"),
      'ovh_doneDate':fields.datetime('donedate',size=256,  required=True, help="Completion date"),
     
               } 


class cloud_service_type_renew(osv.osv):
       #ovh champ SOa internal mane zone serial number  /domain/zone/{zoneName}/soa
       #'service_domain_soa_ids':fields.one2many('cloud.service.domain.soa', 'service_domain_id',"Soa"),     
      _name = 'cloud.service.type.renew'
      _description = 'cloud.service.type.renew'

      _columns = {
        
       'ovh_period':fields.integer('Periode'),
       'ovh_forced':fields.boolean('Forced'),
       'ovh_automatic':fields.boolean('Automatique'),
       'ovh_deleteAtExpiration':fields.boolean('Delete at expiration'),
      
             
               } 
      _defaults = {
                     }
      _order = 'id'

