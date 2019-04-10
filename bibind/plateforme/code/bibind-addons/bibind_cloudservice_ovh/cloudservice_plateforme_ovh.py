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

#
#GET; /hosting/web Beta List available services
# GET; /hosting/web/availableOffer Beta Get available offer
# GET; /hosting/web/moduleList Beta IDs of all modules available
# GET; /hosting/web/moduleList/{id} Beta Get this object properties
# GET; /hosting/web/offerCapabilities Beta Get offer capabilities
# GET; /hosting/web/{serviceName} Beta Get this object properties
# GET; /hosting/web/{serviceName}/attachedDomain Beta Domains or subdomains attached to your hosting
# POST; /hosting/web/{serviceName}/attachedDomain Beta Link a domain to this hosting
# GET; /hosting/web/{serviceName}/attachedDomain/{domain} Beta Get this object properties
# PUT; /hosting/web/{serviceName}/attachedDomain/{domain} Beta Alter this object properties
# DELETE; /hosting/web/{serviceName}/attachedDomain/{domain} Beta Unlink domain from hosting
# GET; /hosting/web/{serviceName}/boostHistory Beta History of your hosting boost
# GET; /hosting/web/{serviceName}/boostHistory/{date} Beta Get this object properties
# GET; /hosting/web/{serviceName}/cron Beta Crons on your hosting
# POST; /hosting/web/{serviceName}/cron Beta Create new cron
# GET; /hosting/web/{serviceName}/cron/{id} Beta Get this object properties
# PUT; /hosting/web/{serviceName}/cron/{id} Beta Alter this object properties
# DELETE; /hosting/web/{serviceName}/cron/{id} Beta Delete cron
# GET; /hosting/web/{serviceName}/database Beta Databases linked to your hosting
# POST; /hosting/web/{serviceName}/database Beta Install new database
# GET; /hosting/web/{serviceName}/database/{name} Beta Get this object properties
# DELETE; /hosting/web/{serviceName}/database/{name} Beta Delete database
# POST; /hosting/web/{serviceName}/database/{name}/changePassword Beta Request a password change
# POST; /hosting/web/{serviceName}/database/{name}/dump Beta Request the dump from your database
# POST; /hosting/web/{serviceName}/database/{name}/request Beta Request specific operation for your database
# GET; /hosting/web/{serviceName}/database/{name}/statistics Beta Get statistics about this database
# GET; /hosting/web/{serviceName}/databaseAvailableVersion Beta List available database version following a type
# GET; /hosting/web/{serviceName}/databaseCreationCapabilities Beta List available database you can install
# GET; /hosting/web/{serviceName}/module Beta Modules installed on your hosting
# POST; /hosting/web/{serviceName}/module Beta Install a new module
# GET; /hosting/web/{serviceName}/module/{id} Beta Get this object properties
# DELETE; /hosting/web/{serviceName}/module/{id} Beta Delete a module installed
# POST /hosting/web/{serviceName}/module/{id}/changePassword Beta Generate a new admin password for your module
# POST; /hosting/web/{serviceName}/request Beta Request specific operation for your hosting
# POST; /hosting/web/{serviceName}/requestBoost Beta Allows you to boost your offer.
# POST; /hosting/web/{serviceName}/restoreSnapshot Beta Restore this snapshot ALL CURRENT DATA WILL BE REPLACED BY YOUR...
# GET; /hosting/web/{serviceName}/serviceInfos Beta Get this object properties
# PUT; /hosting/web/{serviceName}/serviceInfos Beta Alter this object properties
# GET; /hosting/web/{serviceName}/statistics Beta Get statistics about this web hosting
# GET; /hosting/web/{serviceName}/tasks Beta Tasks attached to your hosting
# GET; /hosting/web/{serviceName}/tasks/{id} Beta Get this object properties
# GET; /hosting/web/{serviceName}/token Beta Use to link an external domain. ( This token has to be insert into...
# GET; /hosting/web/{serviceName}/user Beta User allowed to connect into your hosting
# POST; /hosting/web/{serviceName}/user Beta Create new ftp/ssh user
# GET; /hosting/web/{serviceName}/user/{login} Beta Get this object properties
# PUT; /hosting/web/{serviceName}/user/{login} Beta Alter this object properties
# DELETE; /hosting/web/{serviceName}/user/{login} Beta Delete ftp/ssh user
# POST; /hosting/web/{serviceName}/user/{login}/changePassword Beta Request a password change

#



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


_logger = logging.getLogger("bibind_cloudservice")



class cloud_service_plateform (osv.osv):
    _name = 'cloud.service.plateforme'
    _inherit = 'cloud.service'
    _description = 'cloud.service.plateforme'
    
    
    
    
    
    
    
    
    
    def getDomainByAttachedomainList(self, cr, uid, ids, context):
            # create a client using configuration
            zonerecords ={}
            client = ovh.Client(endpoint='ovh-eu')
            
            #validation = client.request_consumerkey(access_rules)
            for plateforme in self.browse( cr, uid, ids, context):
                zone = plateforme.name

            zone = '/hosting/web/%s/attachedDomain'%(zone)
            listDomain = client.get(zone)
       
            return listDomain
        
        
    def getAttachDomainRecordByDomain(self, cr, uid, ids, record, context=None):
            # create a client using configuration
            linerecordid ={}
            client = ovh.Client(endpoint='ovh-eu')
           
            #validation = client.request_consumerkey(access_rules)
            for plateforme in self.browse( cr, uid, ids, context=None):
                zone = plateforme.name
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
                 value['service_plateforme_id']=this.id
         
        value['siteweb_domain']=vale['domain']
        value['siteweb_path']=vale['path']
        value['siteweb_cdn']=vale['cdn']
        
       
       
        return value
    
    def loadRecordDomainServeurDns(self,cr, uid, ids, context):
        
        lines = self.getLineAttacheDomainByRecords( cr, uid, ids, context)
        SdDns = self.pool.get('cloud.service.plateforme.siteweb')
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
    
     # Compute: effective_hours, total_hours, progress
    def _traffic_get(self, cr, uid, ids, field_names, args, context=None):
        res = {}
        
        return res
    
    
    _columns = {
        
        #field ovh  list offre /hosting/web/availableOffer
         'ovh_availableOffer':fields.selection([
                            ("PERFORMANCE_1","PERFORMANCE_1"),
                            ("PERFORMANCE_2", "PERFORMANCE_2"),
                            ("PERFORMANCE_3", "PERFORMANCE_3"),
                            ("PERFORMANCE_4","PERFORMANCE_4"),
                            ( "PERSO", "PERSO"),
                             ( "PRO", "PRO"),
                              ( "START", "START")
                            ], 'Offre possible ovh', size=256, required=True,
                                  help='Hosting\'s offer'),
       

        # field  list /hosting/web/module 
        'service_plateforme_module_ids':fields.one2many('cloud.service.plateforme.module', 'service_plateforme_id',"Module") ,     
        # ovh field  /hosting/web/{serviceName}/request
         'service_plateforme_request_ids':fields.one2many('cloud.service.plateforme.request', 'service_plateforme_id',"Request") ,     
     
        
        
        'Espace_disque_quota':fields.char('Espace disque', size=256 ),
        'trafic_utilise':fields.float('Traffic utilisé'),
        'trafic_quota':fields.char('quota du Trafic ', size=256 ),
        
        'Etat_du_service':fields.char('Etat du service', size=256 ),  
        'Offre':fields.char('Offre', size=256 ),
        'cluster_ipv4':fields.char('Adresse IPV4', size=256 ),
        'cluster_ovh':fields.char('Nom du Cluster', size=256),
        'certificat_ssl':fields.boolean('Certificat SSL', default=False ),
        'option_cdn':fields.boolean('Option CDN', default=False),
        'site_web':fields.char('Site web', size=256),
        'base_donne':fields.char('Base de donnée', size=256 ),
        'Espace_disque_utilise':fields.float('Espace dique utilisé'),
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
        
        
        
        'service_plateforme_countryip_ids':fields.one2many('cloud.service.plateforme.countryip', 'service_plateforme_id',"IP des pays"),   
        
        'availableboostoffer':fields.one2many('cloud.service.plateforme.availableboostoffer', 'service_plateforme_id',"Boost Offer"),   
        #ovh field /hosting/web/{serviceName}/attachedDomain
        'service_plateforme_site_web_ids':fields.one2many('cloud.service.plateforme.siteweb', 'service_plateforme_id',"Zone DNS Lines"),   
        
        #ovh field /hosting/web/{serviceName}/cron 
        'service_plateforme_cron_ids':fields.one2many('cloud.service.plateforme.cron', 'service_plateforme_id',"Cron Lines"),   
       
        'service_plateforme_bdd_ids':fields.one2many('cloud.service.plateforme.sql', 'service_plateforme_id',"Base de donnée line") ,     
        'service_plateforme_ftp_ids':fields.one2many('cloud.service.plateforme.ftp', 'service_plateforme_id',"compte FTP") ,     
      
        
                }
    
####################action sur le service plateforme création de task ovh####################
    
    #installation d'un module /hosting/web/{serviceName}/module 
    def install_module(self,cr, uid, ids,value, context):
        
        return True
    
    #change password module admin  /hosting/web/{serviceName}/module/{id}/changePassword 
    def change_password_module(self,cr,uid,ids,value,contex):
        
        return True
    
    #action cahe /hosting/web/{serviceName}/request   CHECK_QUOTA FLUCH_CACHE SCAN_ANTIHACK
    def lance_action_request_cache(self,cr,uid,ids,value, context):
        
        return True
    
    def lance_action_request_quota(self,cr,uid,ids,context):
        
        return True
        
    def lance_action_request_scan(self,cr,uid,ids,context):
        
        return True
    # action boost pour performance /hosting/web/{serviceName}/requestBoost 
    def lance_action_requestBoost(self,cr,uid,ids,context):
        
        return True
    
    
     
    
    # restore data /hosting/web/{serviceName}/restoreSnapshot
    def lance_action_restoreSnapshot(self,cr,uid,ids,context):
        
        return True
    
    
    # create user ftp/ssh etc /hosting/web/{serviceName}/user
    def lance_action_create_user_ftp(self,cr,uid,ids,context):
        
        return True
    
    
    
    #action change password login/hosting/web/{serviceName}/user/{login}/changePassword   
    
    def lance_action_changepassword_user_ftp(self,cr,uid,ids,context):
        
        return True
    
    #action création d'une databas /hosting/web/{serviceName}/database 
    def lance_action_create_database(self,cr,uid,ids,values, context):
        
        return True
    
    # change password database  /hosting/web/{serviceName}/database/{name}/changePassword 
    def lance_action_change_password_database(self,cr,uid,ids,databasename, password, context):
        
        return True
     # dump  database   /hosting/web/{serviceName}/database/{name}/dump 
    def lance_action_database_dump(self,cr,uid,ids, databasename, date, context):
        
        return True
    
     #database check quota  /hosting/web/{serviceName}/database/{name}/request 
    def lance_action_database_request_quota(self,cr,uid,ids,databasename, action,context):
        
        return True
#########################################################################

#################### Statistique sur le service plateforme ####################
 
    #statistique sur sql base de donnée /hosting/web/{serviceName}/database/{name}/statistics
    def get_database_statistique(self,cr,uid,ids,databasname, type, context):
        
        return True
    
    
    
    #statistique sur le servrice /hosting/web/{serviceName}/statistics 
    
    def get_hosting_statistique(self,cr,uid,ids, type, context):
        
        return True
    
 
####################################################################################
   
    def _getValueTraffic(self, content):
         
         if not content.get('value'):
             return 100
           
         return content.get('value')

    def _getValueSpace(self, content):
         
         if not content.get('value'):
             return 100
           
         return content.get('value')

    def _getValueUsedTraffic(self, total, content):
         
         if not content.get('value'):
             return 33
         
         Total = total.get('value')
         val = content.get('value')
         pourcent = (val*100)/Total
         return pourcent
     
     
     
    def _getValueUsedSpace(self, total, content):
         
         if not content.get('value'):
             return 100
         if(total.get('unit')==content.get('unit')):
             Total = total.get('value')
             val = content.get('value')
             pourcent = (val*100)/Total
         else:
              if(total.get('unit')=='GB' and content.get('unit')=='MB' ):
                  Total = total.get('value')
                  val = content.get('value')/1000
                  pourcent = (val*100)/Total
         
         return pourcent    
    
    
    def is_Plateform_exit(self, name):
        client = ovh.Client(endpoint='ovh-eu')
        path =  '/hosting/web/s%'%(name)
        content = client.get(path)
        return content
    
    
    def LoadPlatforme(self, cr, uid, name, context):
          
            value ={}
            
            client = ovh.Client(endpoint='ovh-eu')
            path =  '/hosting/web/s%'%(name)
            content = client.get(path)
            _logger.info('this quota  %s' % (content['quotaSize']))
            _logger.info('this traf  %s' % (content['trafficQuotaSize']))
            _logger.info('this traf used  %s' % (content['trafficQuotaUsed']))
            _logger.info('this space used  %s' % (content['quotaUsed']))
            
            value['name']=content['serviceName']
            value['Espace_disque_quota']=self._getValueSpace(content['quotaSize'])
            value['trafic_utilise']=self._getValueUsedTraffic(content['trafficQuotaSize'],content['trafficQuotaUsed']) #content['quotaUsed']
            value['trafic_quota']=self._getValueTraffic(content['trafficQuotaSize'])
            value['Etat_du_service']=content['state']
            value['Offre']=content['offer']
            value['cluster_ipv4']=content['clusterIp']
            value['cluster_ovh']=content['cluster']
            value['certificat_ssl']=content['hasHostedSsl']
            value['option_cdn']=content['hasCdn']
            
            
            value['Espace_disque_utilise']= self._getValueUsedSpace(content['quotaSize'],content['quotaUsed'])
            value['filer']=content['filer']
            value['serveur_ftp']=content['hostingIp']
            value['login_ftp_principal']=content['primaryLogin']
            value['log_text']=content['primaryLogin']
            #value['service_plateforme_countryip_ids']=content['countriesIp']
           
            value['path_home']=content['home']
            value['boostoffer']=content['boostOffer']
            value['hostingipv6']=content['hostingIpv6']
            #value['availableboostoffer']=content['availableBoostOffer']
            value['resourcetype']=content['resourceType']
            value['systemeos']=content['operatingSystem']
            value['clusteripv6']=content['clusterIpv6']
            
            return value
    
    
    
    
    
    def BeforeCreatePlateforme(self, cr, uid, vals, context):
        value = self.LoadPlatforme(cr, uid, vals.name, context)
        return value
    
    
    def is_automatique_create(self,cr, uid, vals, context):
        
        return True
    
    
    
    def create(self, cr, uid, vals, context):
        auto = self.is_automatique_create( cr, uid, vals, context)
        if auto:
            vals = self.BeforeCreatePlateforme(cr, uid, vals, context)
        
        res = super(cloud_service_plateform, self).create(cr, uid, vals, context)
       
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        # if alias_model has been changed, update alias_model_id accordingly
        return super(cloud_service_plateform, self).write(cr, uid, ids, vals, context=context)

    
    def checkPlatforme(self, cr, uid, ids, context):
            for this in self.browse(cr, uid, ids, context):
                 _logger.info('this id  %s' % (this.id))
      
            value ={}
            client = ovh.Client(endpoint='ovh-eu')
            path =  '/hosting/web/asagimbert.com' 
            content = client.get(path)
            _logger.info('this quota  %s' % (content['quotaSize']))
            _logger.info('this traf  %s' % (content['trafficQuotaSize']))
            _logger.info('this traf used  %s' % (content['trafficQuotaUsed']))
            _logger.info('this space used  %s' % (content['quotaUsed']))
            value['name']=content['serviceName']
            value['Espace_disque_quota']=self._getValueSpace(content['quotaSize'])
            value['trafic_utilise']=self._getValueUsedTraffic(content['trafficQuotaSize'],content['trafficQuotaUsed']) #content['quotaUsed']
            value['trafic_quota']=self._getValueTraffic(content['trafficQuotaSize'])
            value['Etat_du_service']=content['state']
            value['Offre']=content['offer']
            value['cluster_ipv4']=content['clusterIp']
            value['cluster_ovh']=content['cluster']
            value['certificat_ssl']=content['hasHostedSsl']
            value['option_cdn']=content['hasCdn']
            
            
            value['Espace_disque_utilise']= self._getValueUsedSpace(content['quotaSize'],content['quotaUsed'])
            value['filer']=content['filer']
            value['serveur_ftp']=content['hostingIp']
            value['login_ftp_principal']=content['primaryLogin']
            value['log_text']=content['primaryLogin']
            #value['service_plateforme_countryip_ids']=content['countriesIp']
           
            value['path_home']=content['home']
            value['boostoffer']=content['boostOffer']
            value['hostingipv6']=content['hostingIpv6']
            #value['availableboostoffer']=content['availableBoostOffer']
            value['resourcetype']=content['resourceType']
            value['systemeos']=content['operatingSystem']
            value['clusteripv6']=content['clusterIpv6']
        #'service_plateforme_site_web_ids':   
        #'service_plateforme_bdd_ids':     
        #'service_plateforme_ftp_ids':     
            
            #r = a.safe_call('catalog.list',product_spec)
           # r = a.safe_call('domain.available', ['terres-ile-chauvet.fr'])

            #var = self.getLineAttacheDomainByRecords(cr, uid, ids, context)
            self.write(cr, uid, ids,  value, context=context)
       
            return True


class cloud_service_plateforme_countryip(osv.osv):    
    _name ='cloud.service.plateforme.countryip'
    _description ='cloud.service.plateforme.countryip'
    
    _columns = {
         'countryip_pays':fields.char('pays', required=True),
        
        'countryip_ip':fields.integer('ip',  required=True),
        
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 
    
    
class cloud_service_plateforme_availableboostoffer(osv.osv):    
    _name ='cloud.service.plateforme.availableboostoffer'
    _description ='cloud.service.plateforme.availableboostoffer'
    
    _columns = {
         'offre':fields.char('type d\'offre', required=True),
        
        'price':fields.integer('price',  required=True),
        
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 

   
    
class cloud_service_plateforme_siteweb(osv.osv):    
    _name ='cloud.service.plateforme.siteweb'
    _description ='cloud.service.plateforme.siteweb'
    
    _columns = {
        
        'siteweb_domain':fields.char('Serveur DNS', size=256, required=True),
        'siteweb_path':fields.char('Chemin du site', size=256, required=True),
        'siteweb_cdn':fields.char('CDN Etat', size=256, required=True),
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 






class cloud_service_plateforme_sql(osv.osv):    
    _name ='cloud.service.plateforme.sql'
    _description ='cloud.service.plateforme.sql'
    
    _columns = {
                

        'ovh_quotaSize':fields.char('Space allowed',  required=True,
                                    help="Space allowed"),
        'ovh_quotaUsed':fields.char('Space used', size=256, required=True,
                                    help="Space used"),
        'ovh_mode':fields.selection([
                                    ("besteffort","besteffort"),
                                   ( "classic","classic"),
                                    ],'Mode of your database', size=256, required=True,
                               help="Mode of your database"),
        'ovh_version':fields.selection([
                                ("4.0","4.0"),
                                ("5.1","5.1"),
                                ("5.5","5.5"),
                                ("8.4","8.4")
                                ],'Database version following the database type', size=256, 
                                  required=True,
                                  help="Database version following the database type"),
        
        'ovh_name':fields.boolean('Database name', default=False, required=True,
                                  help="Database name"),
        'ovh_port':fields.char('port', size=256, help="The port on where to contact this database"),
        'ovh_state':fields.selection([
                                ("close","close"),
                                ("ok","ok"),
                                ("readonly","readonly")
                              
                                ],'Etat', size=256, required=True,
                                help="Database state"),
        'ovh_user':fields.char('user', size=256, required=True,
                               help="Database user name"),
        'ovh_type':fields.selection( [
                                ("mysql","mysql"),
                                ("postgresql","postgresql")
                                ],'Type de base de donnée', size=256, required=True),
        'ovh_server':fields.char('server', size=256, readonly=True,
                                 help="Your database server name"),
      
         
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 






class cloud_service_plateforme_ftp(osv.osv):    
    _name ='cloud.service.plateforme.ftp'
    _description ='cloud.service.plateforme.ftp'
    
    _columns = {
        
        'ftp_login':fields.char('Login', size=256, required=True),
        'ftp_repertoir':fields.char('Repertoire', size=256, required=True),
        'ftp_etat':fields.boolean('Etat', default=False, required=True),
        'ftp_ovh_id':fields.integer('id ovh api',  required=True),
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 


class cloud_service_plateforme_cron(osv.osv):    
    _name ='cloud.service.plateforme.cron'
    _description ='cloud.service.plateforme.cron'
    
    _columns = {
      
        
        'ovh_email':fields.char('Email', size=256, 
                                help="Email use to receive error log ( stderr )"),
        'ovh_frequency':fields.char('Chemin du site', size=256,
                                    help="Frequency ( crontab format ) defined for the script ( minutes are ignored )"),
        'ovh_language':fields.selection( [
                                    ("other","other"),
                                    ("php4","php4"),
                                    ("php5.2","php5.2"),
                                    ("php5.3","php5.3"),
                                    ("php5.4","php5.4"),
                                    ("php5.5","php5.5"),
                                    ("php5.6","php5.6")
                                    ],
                                        'Cron\'s language', size=256, required=True),
        
        'ovh_id':fields.integer("Cron's id", required=True,
                                help="Cron's id"),
        'ovh_description':fields.text("description",  required=True,
                                      help="Description field for you"),
        'ovh_command':fields.char('Command to execute', size=256, required=True,
                                  help="Command to execute"),
         
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 




class cloud_service_plateforme_module(osv.osv):    
    _name ='cloud.service.plateforme.module'
    _description ='cloud.service.plateforme.module'
    
    _columns = {
       'ovh_language':fields.selection([
                               ( "cz","cz"),
                                ("de","de"),
                                ("en","en"),
                                ("es","es"),
                                ("fi","fi"),
                                ("fr","fr"),
                                ("it","it"),
                                ("lt","lt"),
                                ("nl","nl"),
                                ("pl","pl"),
                                ("pt","pt")
                                ], 'Install language', size=256, required=True ,help="All available languages for this module"),
        'ovh_dependencies':fields.char('Type de dépendances', required=True,
                                       help="The dependencies to which the module has access. A dependency can be a standard database (like MySQL or PostgreSQL) or a key-value store (like Redis or Memcached) for example"),
        'ovh_path':fields.char('Path', size=256, required=True,
                                help="Where the module is installed, relative to your home directory"),
        'ovh_moduleId':fields.integer('Module ID', size=256, required=True,
                                       help="ID of the module associated with this installation"),
        'ovh_targetUrl':fields.char('Target url', size=256, required=True,
                                    help="The URL from where your module can be reached"),
        'ovh_lastUpdate':fields.datetime('Last update', size=256, required=True,
                                         help="Date of the last module's upgrade"),
        'ovh_creationDate':fields.datetime('Date d\'installation', size=256, required=True,
                                       help="Date of the installation of the module"),
        'ovh_adminName':fields.char('Admin name', size=256, required=True,
                                    help="Login for the admin account"),
        'ovh_id': fields.integer('id installation', required=True,
                              help="Installation ID"),
        'ovh_adminFolder':fields.char('admin folder', size=256, required=True,
                                      help="The admin folder, relative to the module's installation path"),
        'password':fields.char('password', size=256,help="password pour l'admin cms modul"),
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 


class cloud_service_modulelist(osv.osv):    
    _name ='cloud.service.modulelist'
    _description ='cloud.service.modulelist'
    
    _columns = {
        
        'ovh_language':fields.selection([
                               ( "cz","cz"),
                                ("de","de"),
                                ("en","en"),
                                ("es","es"),
                                ("fi","fi"),
                                ("fr","fr"),
                                ("it","it"),
                                ("lt","lt"),
                                ("nl","nl"),
                                ("pl","pl"),
                                ("pt","pt")
                                ], 'Install language', size=256, required=True ,help="All available languages for this module"),
        'ovh_latest':fields.boolean('is latest version', default=False, help="Is this the latest version available?"),
        'ovh_version':fields.char('version', size=256, required=True, help="The version of the module"),
        'ovh_name':fields.char('name',size=256,  required=True, help="name of the module"),
        'ovh_active':fields.boolean('Is the module available?', default=False, help="Is the module available?"),
        'ovh_adminNameType':fields.selection([
                               ( "email","email"),
                                ("string","string")
                               
                                ], 'The type of the admin name', size=256, required=True ,help="The type of the admin name"),
       
        'ovh_author':fields.char('author',size=256,  required=True, help="The packager of this module for OVH"),
        'ovh_branch':fields.char('branch',size=256,  required=True, help="The branch of the module"),
        'ovh_upgradeFrom':fields.char('module upgrade', help="All the IDs of other modules this module can upgrade"),
        'ovh_size':fields.char('Size of the module',size=256,  required=True, help="The branch of the module"),
        'ovh_keywords':fields.char('The keywords for this module',size=256,  required=True, help="The keywords for this module"),
        'ovh_id':fields.integer('The ID of the module', help="The ID of the module"),
        
        'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 
    

class cloud_service_plateforme_task(osv.osv):    
    _name ='cloud.service.plateforme.task'
    _description ='cloud.service.plateforme.task'
    
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
      'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 

class cloud_service_plateforme_request(osv.osv):    
    _name ='cloud.service.plateforme.request'
    _description ='cloud.service.plateforme.resquest'
    
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
      'service_plateforme_id':fields.many2one('cloud.service.plateforme',"Plateforme", required=True),
            
               } 

    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
