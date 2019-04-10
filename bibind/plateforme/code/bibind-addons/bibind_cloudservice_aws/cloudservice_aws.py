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
############################################################################
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time, os, random, string
from openerp import pooler
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
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
import urllib2

from pygments.lexer import _inherit
from _mysql import result
from sphinx.domains import Domain

## parser
import requests

from socket import getaddrinfo

_logger = logging.getLogger("dedaluvia_cloudservice_ovh")





#module aws
class cloud_service_api_fournisseur_aws(models.Model):
    _inherit = 'cloud.service.api.fournisseur'
   
    
    
    api_ref= fields.Reference(selection_add=[('cloud.service.api.aws','api aws')] )
        
    
cloud_service_api_fournisseur_aws()

#api crée specifiquement pour ovh
class Cloud_Service_api_aws(models.Model):
    _name = 'cloud.service.api.aws'
    
    
    name= fields.Char('nom', size=255)
    fournisseur = fields.Many2one('res.partner',)
    description= fields.Char('description', size=255)
    region= fields.Selection(selection=[('us-east-1','us-east-1'),
                                          ('cn-north-1','cn-north-1'),
                                          ('ap-northeast-1','ap-northeast-1'),
                                          ('eu-west-1','eu-west-1'),
                                          ('ap-southeast-1','ap-southeast-1'),
                                          ('ap-southeast-2','ap-southeast-2'),
                                          ('us-west-2','us-west-2'), 
                                          ('us-gov-west-1','us-gov-west-1'),
                                          ('us-west-2','us-west-2'),
                                          ('us-west-1','us-west-1'),
                                          ('eu-central-1', 'eu-central-1'),
                                          ('sa-east-1','sa-east-1')
                                          ],
                                           string='Endpoint',
                                           help='choisir l\'endpoint' )
    compteiam = fields.Char('Compte IAM')
    motdepasse = fields.Char('Mot de passe du Nichandle')
    file_conf = fields.Binary('ficher de configuration')
    access_key_id=fields.Char('Application key')
    sshkeyid=fields.Char('Application secret')
    consumer_key=fields.Char('Consumer key')
    requete_is_import = fields.Boolean('Liste des urls importée', default=False, readonly=True)
    
      
    ##list_url = fields.Selection(selection='getlist_api_order_Url', string='List ovh des commandes')
    
    #requeteapiids = fields.One2many('cloud.service.api.url.requete','apiovhid',  string='Requete url et param possible pour ovh',ondelete='cascade', required=True)
   
   
    
    @api.model
    @api.multi
    def _get_default_wpartner(self):
       
        res_part = self.env['res.partner']
        domain = [('name','=', 'OVH'),('supplier','=',True)] # condition
        res = res_part.search(domain, limit=1)
        
        return res
       
    def traitement_url(self, url, param):
        
        traitement = {}
        reste = {}
        for k in param:
            if url.find(k)!=-1:
                url = url.replace('{'+k+'}', p[k])
            else :
               
                reste[k]=p[k]
        traitement['url'] = url
        traitement['praram'] = reste
        return traitement 
    
    def traitement_param(self, url, requete_param_api, paramclient):
        
         requet_param_ids = self.env['cloud.service.requete.param'].browse(requete_param_api)
         param ={}
         for requet_param_id in requet_param_ids:
             if requet_param_id.is_enum and not requet_param_id.is_client_param:
                 param[requet_param_id.name]= requet_param_id.enum_valeur
             else :
                 param[requet_param_id.name]= requet_param_id.valeur
             for p in paramclient:
                if requet_param_id.is_client_param and requet_param_id.name==p:
                    param[requet_param_id.name]=paramclient[p]
                    
                    
         return param
    
    def _connection_aws(self):
        
        conn = boto.ec2.connect_to_region(self.region,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.sshkeyid)
        
        return conn
    
    
    def callcreateservice(type_service, url, requete_param_api, paramclient, obj_service_fournisseur ):
        
        con = self._connection_aws()
        
        param =self.traitement_param(url, requete_param_api, paramclient)
       
      
        res = con.run_instances(param)
        instance = res.instances[0]
        
        retour_host = self.post_traitement_param_host(con, res)
       
        return retour_host
    
    
    
            
    def post_traitement_param_host(self, conn, reservation):
        
        reservation  = conn.get_all_instances(instance_ids=['i-c2aac37b'])
        instances = [i for r in reservation for i in r.instances]

        #instance = reservation[0].instances[0]
        host = {}
        for i in instances:
            host['region'] = i._placement
            host['ip_publique'] = i.ip_address
            host['dns_public'] = i.public_dns_name
            host['ip_prive'] = i.private_ip_address
            host['dns_prive'] = i.private_dns_name
            host['root_device_name'] = i.root_device_name
            host['root_device_type'] =i.root_device_type
            host['vpc_id'] = i.vpc_id
            
            host['group_name'] = i.group_name
        
        return host
    
    
    def create_domain(self, url, requete_param_api, paramclient, obj_service_fournisseur ):
        
        domain = paramclient['domain']
        #domainCheck
        session = self.soap.login(self.nichandle, self.motdepasse, 'fr', 0)
        
        
        result =self.soap.resellerDomainCreate(
                                          session, 
                                          domain, 
                                          'none', 
                                          'gold', 
                                          'none', 
                                          'yes', 
                                          self.nichandle, 
                                          self.nichandle, 
                                          self.nichandle, 
                                          self.nichandle, 
                                          'dns17.ovh.net', 
                                          'ns17.ovh.net', 
                                          '', 
                                          '', 
                                          '', 
                                          '', 
                                          '', 
                                          '', 
                                          '',
                                          '', 
                                          '', 
                                          '', 
                                          '',
                                           1, 
                                          '', 
                                          '',
                                           'cdnBasic')
        #logout
        self.soap.logout(session)
        if result==None:
            res = domain
        else:
            res = False
        return res
    
    def create_mutualise(self, url, requete_param_api, paramclient, obj_service_fournisseur ):
        
        client = ovh.Client(endpoint=self.endpoint)
           
        param =self.traitement_param(url, requete_param_api, paramclient)
        traitement = self.traitement_url(url, param)
        
        try:
            res = client.post(traitement['url'], traitement['param'])
        except:
            res = False
        return res
        
        
    
    def create_dedie(self, url, requete_param_api, paramclient, obj_service_fournisseur ):
        
        
        
        return True
    
    
    
    def create_vm(self, url, requete_param_api, paramclient, obj_service_fournisseur ):
        
        
        
        return True
    
    
    
    
    def call_verif_domain_info(self, domain):
        
        client = ovh.Client(endpoint=self.endpoint)
        zone ='/domain/%s/serviceInfos ' %(domain)
        res = client.get(zone)['status']
        if res =='ok' or res=='inCreation':
            return True
        else :
            return False
    
    def call_get_order(self,type_service,url, requete_param_api,  paramclient, retour_api_param_service, obj_service_fournisseur ):
        
        return data_order
    
    def call_get_param_host(self, type_service,url, requete_param_api,  paramclient, retour_api_param_service, objet_service_fournisseur):
        
        return param_host
    
    
    
    def call_verif_order (self, url, param, retour_paramet): 
        
        
        client = ovh.Client(endpoint=self.endpoint)
        url = self.traitement_url(url, param)
        param =self.traitement_param(url, param)
        
        res = client.post(url, param)
        if res :
            return True
        return False 
        
        
   
    
   
             
             
                 
            
             
            
    
    
    def get_paramhost(self,type):
        
        client = ovh.Client(endpoint=self.endpoint)
        zone ='/hosting/web/%' %(domain)
        res = client.get(zone)['status']
        
        return res
    
   
    @api.multi
    def getlist_api_order_Url(self):
         url = ENDPOINTS[self.endpoint]+'/order.json'
         apijsonorder = requests.get(url).json()
         #_logger.info('api   %s' % (apijsonorder))
         res =[]
         for api in apijsonorder['apis']:
            for http in api['operations']:
                if http['httpMethod']=="POST":
                    _logger.info('api   %s' % (api['path']))
                    res.append((api['path'], api['path'] + ' : '+api['description']))
                   
        
         return res
     
    @api.multi
    def import_requetUrl(self):
        url = ENDPOINTS[self.endpoint]+'/order.json'
        apijsonorder = requests.get(url).json()
        obj_requete = self.env['cloud.service.api.url.requete']
        #_logger.info('get function fournisseur   %s' % (self._get_default_wpartner()))
        if not self.fournisseur:
            fournisseur = self._get_default_wpartner()
        else :
            fournisseur = self.fournisseur    
        res =[]
       
        val = {'fournisseur':fournisseur.id}
        for api in apijsonorder['apis']:
            for http in api['operations']:
                if http['httpMethod']=="POST":
                    val_id = {}
                    val_id['param'] =http['parameters']
                    for pam in http['parameters']:
                        valpam= pam['dataType']
                        if isinstance(valpam, basestring):
                            if valpam in apijsonorder['models']:
                              val_id[valpam] =apijsonorder['models'][valpam]
                              
                    val.update({'name':api['path'],
                                'url':api['path'],
                                'endpoint':self.endpoint,
                                'data_json':json.dumps(val_id),
                                'description':http['description'],
                                })
                    
                    obj_requete.create(val) 
                    
        self.requete_is_import = True     
        return  True
     
    @api.multi
    def delete_import_requetUrl(self):
        
        obj_requete = self.env['cloud.service.api.url.requete']
        requetes = obj_requete.search([('endpoint','=',self.endpoint)])
        for r in requetes:
            r.unlink()
        self.requete_is_import = False
          
            
        return  True
    @api.multi
    def test_attachment_by_url(self):
           #url = 'https://www.ovh.com/cgi-bin/order/displayOrder.cgi?orderId=39335072&orderPassword=sxog'
            url ='https://www.ovh.com/cgi-bin/order/bill.pdf?reference=FR13893286&passwd=8VAI'
            
            attachment = self.env['ir.attachment']
            document_vals = {'name': 'maco.pdf',

                             'url': url,

                             'res_model': self._name,

                             'res_id': self.id,

                             'type': 'url' }
            response = urllib2.urlopen(url)
            result  = response.read().encode('base64')
            
           
            
            doc_val = {
                   'name': 'montest.pdf',
                    'datas': result,
                    'datas_fname': 'montest.pdf',
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary'

                   
                   }
            
            attachment.create(doc_val)
            
            return False
     
     
     
    def create_requete_api_url(self):
        
        return
        
        
        
Cloud_Service_api_aws()

class cloud_service_api_url_requete(models.Model):
        _inherit = 'cloud.service.api.url.requete'
        
       
        apiovhid=fields.Many2one('cloud.service.api.ovh', 'Api ovh')
        endpoint =fields.Char('Endpoint', readonly=True)
        fournisseur_name =fields.Char('nom fournisseur')
        #type= fields.Selection('(list de champs possible)'),
        #html= fields.html('(mettre la valeur html)'),
        #valeur_du_champs= fields.Char('valeur du champs'),
        
        
        
        @api.multi
        @api.onchange('fournisseur')
        def onchange_fournisseur(self):
            self.fournisseur_name = self.fournisseur.name
        
        
        
        def create(self, values):
            if values.get('fournisseur'):
                fname = self.env['res.partner'].browse(values.get('fournisseur'))['name']
                values.update({'fournisseur_name':fname})
            
            new_id = super(cloud_service_api_url_requete, self).create(values)
            return new_id
            
    
cloud_service_api_url_requete()

class Cloud_Service_tmpl(models.Model):
        _inherit = 'cloud.service.tmpl'
   
            
        instance_de_gestion= fields.Reference(selection_add=[('cloud.service.instance.service', '')])
    
Cloud_Service_tmpl()


class cloud_service_tmpl_fournisseur(models.Model):
        _inherit = 'cloud.service.tmpl.fournisseur'

        @api.multi
        @api.depends('fournisseur_id')
        def config_url_param(self):
            res = super(cloud_service_tmpl_fournisseur, self).config_url_param()
            if self.fournisseur_id.name=='OVH':
                        
                requete = self.requete_api_service 
                obj_model = self.env['cloud.service.param.model']
                obj_param = self.env['cloud.service.requete.param']
                if self.requete_api_service:
                    j = requete.data_json
                    req = json.loads(j)
                    _logger.info('data  jsone %s' % (req))
                    if req['param']:
                        for datatype in req['param']:
                            #_logger.info('datatype in boucle  jsone %s' % (datatype))
                            param_val = {
                                         'name':datatype['name'],
                                         'datatype':datatype['dataType'],
                                         'paramtype':datatype['paramType'],
                                         'is_requiered':datatype['required'],
                                         'description':datatype['description'],
                                         'url_id':self.requete_api_service.id,
                                         'tmpl_fournisseur_id':self.id,
                                         }
                            _logger.info('param_val in boucle  jsone %s' % (param_val))
                            obj_param.create(param_val)
                            if datatype['dataType'] in req:
                                nb = obj_model.search([('modeltype','=',datatype['dataType'])])
                                _logger.info('nb jsone %s' % (nb))
                                if not nb :
                                    
                                    for mo in req[datatype['dataType']]['enum']:
                                        _logger.info('mo  jsone %s' % (mo))
                                        _logger.info('datatype description  jsone %s' % (req[datatype['dataType']]['description']))
                                        _logger.info('data type jsone %s' % (datatype['dataType']))
                                        val ={'name':mo,
                                         'description':req[datatype['dataType']]['description'],
                                         'modeltype':datatype['dataType'],
                                         }
                                        _logger.info('data val  jsone %s' % (val))
                                        obj_model.create(val)
                                        
            return True
            
            
        
