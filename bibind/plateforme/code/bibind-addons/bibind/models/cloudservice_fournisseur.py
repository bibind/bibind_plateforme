# -*- encoding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
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

from odoo import SUPERUSER_ID

from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import odoo.addons.decimal_precision as dp
from odoo import netsvc
from odoo import models, fields, api, _
import logging
import json
import re
from lxml import etree
import paramiko
from paramiko import SSHClient
import ovh
from socket import getaddrinfo
import requests
import sys
from libcloud.compute.types import Provider
from libcloud.compute.providers import DRIVERS
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment, SSHKeyDeployment
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


_logger = logging.getLogger("bibind_cloudservice")

class bibind_host_group(models.Model):
        _name = 'bibind.host.group'
   
        name = fields.Char('nom', size=128)
        parent_id = fields.Many2one('bibind.host.group', string='Parent group', select=True, ondelete='cascade')
        child_id = fields.One2many('bibind.host.group', 'parent_id', string='Child group')
        
        sequence = fields.Integer(string='Sequence', select=True)
    
    
bibind_host_group()


class cloud_service_host(models.Model):
        _name = 'bibind.host'
        
        def _get_state_node(self):
            st = [( 'NONODE' , 'Not link'),
                    ( 'RUNNING' , 'running'),
                  ('STARTING' , 'starting'),
                    ('REBOOTING' , 'rebooting'),
                    ('TERMINATED' , 'terminated'),
                    ('PENDING' , 'pending'),
                   ( 'UNKNOWN' , 'unknown'),
                    ('STOPPING' , 'stopping'),
                    ('STOPPED' , 'stopped'),
                    ('SUSPENDED' , 'suspended'),
                    ('ERROR' ,'error'),
                    ( 'PAUSED' , 'paused'),
                    ('RECONFIGURING' , 'reconfiguring'),
                    ('MIGRATING' , 'migrating'),
                    ('NORMAL' , 'normal')]
            return st
        
        
        def _default_state_host(self):
            _logger.info('defaul nodeid %s' % (self.nodeid))
            if self.nodeid:
                return self.nodeid.state
            else :
                return 'NONODE'
        
        name= fields.Char('Name')
        nodeid = fields.Many2one('cloud.service.node', string="node")
        host_ipv4 = fields.Char('Adress ipv4', related='nodeid.public_ips')
        host_ipv6 = fields.Char('Adress ipv6')
        hostname = fields.Char('Hostname', related='nodeid.name')
        state = fields.Selection(selection='_get_state_node',string='State',related='nodeid.state', default=_default_state_host )
        image = fields.Many2one('cloud.service.nodeimage', string='Image')
        size = fields.Many2one('cloud.service.nodesize', string='Size')
        location = fields.Many2one('cloud.service.nodelocation')
        deploy_scripts_ids = fields.Many2many('launch.script', string='Scripts de déploiement')
        group = fields.Many2one('bibind.host.group')
        scriptdeployed = fields.Char(string='Ids script deployed')
        deployed = fields.Boolean('host' ,default=False)
        docker_rancher_deployed = fields.Boolean('Docker is installed' ,default=False)
        rancher_deployed = fields.Boolean('Rancher command installed' ,default=False)
        log = fields.Text('log')

        @api.onchange('nodeid')
        def get_state_with_node(self):
            _logger.info('nodeid %s' % (self.nodeid))
            _logger.info('state %s' % (self.state))
            _logger.info('nodieid state %s' % (self.nodeid.state))
            if self.nodeid:
                self.state = self.nodeid.state
                self.location = self.nodeid.location.id
                self.size = self.nodeid.size.id
                self.image = self.nodeid.image.id
            else :
                self.state = 'NONODE'
        
        

        def destroy_node(self):
            if self.nodeid:
                delete = self.nodeid.destroy_node()
                if(delete):
                    self.state = 'TERMINATED'
        

        def script_deployed(self):
            
            deplo ={}
            for script in self.deploy_scripts_ids:
                deplo[script.id] = script.id
            
            self.scriptdeployed = json.dumps(deplo)
            


        def script_is_deployed(self):
            notedploy = []
            _logger.info('context script  id %s' % (json.loads(self.scriptdeployed)))
            for script in self.deploy_scripts_ids:
                                    
                if not any(str(script.id) in s for s in json.loads(self.scriptdeployed)):
                    notedploy.append(script.id)
            if len(notedploy)==0:
                self.log = 'tous les scripts'
            else :
                self.log = notedploy
                

        def button_script_is_deployed(self, script):
                        
            if not any(str(script.id) in s for s in json.loads(self.scriptdeployed)):
                   return False
            else :
               return True
            

        def deployer_script_notinstalled(self, script):
            
            _logger.info('context script notinstalled  name %s' % (script.name))
            api =self.nodeid.api_driver
            rep = api.deploy_specific_script(self, script)
            _logger.info('context script notinstalled  return %s' % (rep))
            if rep:
                return rep
            

        def deployer_script_install_docker(self, script):
            
            script = self.env.ref('bibind.script_install_docker_rancher')
            _logger.info(' script load  id %s' % (script.name))
            api =self.nodeid.api_driver
            rep = api.deploy_specific_script(self, script)
            _logger.info('context script notinstalled  return %s' % (rep))
            if rep:
                self.log = rep
                return rep
        

        def deployer_script_is_docker_exist(self):
            
            script = self.env.ref('bibind.script_is_docker_exist')
            _logger.info(' script load  id %s' % (script.name))
            api =self.nodeid.api_driver
            rep = api.deploy_specific_script(self, script)
            _logger.info('context script notinstalled  return %s' % (rep))
            if rep:
                self.log = rep
                return rep
            
        @api.depends('state')
        def _deployed(self):
            if any(self.state in s for s in ['RUNNING','STARTING', 'TERMINATED']):
                self.deployed = True
            else :
                self.deployed = False
        
        def copy_host_param_ansible_config(self):
            
            return file
            
        
        
cloud_service_host()


class Cloud_Service_fournisseur(models.Model):
        _name = 'cloud.service.fournisseur'
        _inherit = ['mail.thread', 'mail.activity.mixin']
        
        
        
        
        name= fields.Char('nom',size=128, default="/")
        created= fields.Date('date de création')
        expired= fields.Date('date dexpiration')
        
        fournisseur= fields.Many2one('res.partner', required=True)
        fournisseur_api= fields.Many2one('cloud.service.api.fournisseur', required=True)
        
       
        host_ids = fields.Many2many('bibind.host',  string="Hosts")
        
        product_id= fields.Many2one('product.template' , required=True)
        is_paid =fields.Boolean('Service payé')
        is_domain = fields.Boolean('Is domain service')
        domain = fields.Char('Nom de domain')
        is_depend_domain = fields.Boolean('Ce service depend d un domain')
        domain_main = fields.Char('Domain principal')
        service_fournisseur_domain_id = fields.Many2one('cloud.service.fournisseur', 'Service fournisseur domain dont dÃ©pend ce service')
        type_service = fields.Selection(selection=([
                                                    ('domain', 'Service domain'),
                                                    ('mutualise','Service Mutualisé'),
                                                    ('dedie_mutualise','Service Dédié Mutualisé'),
                                                    ('vm_mutualise','Service Virtual Machine pour Mutualisé'),
                                                    ('dedie','Service Serveur dédié'),
                                                    ('vm','Service Machine virtuel'),
                                                    ('infrastructure','Service infrastructure'),
                                                    ]))
        
        
        category = fields.Many2one('cloud.service.category')
        cloud_service_ids= fields.One2many('cloud.service', 'cloud_service_fournisseur_id', string='service client')
        availaible_service = fields.Integer(string='Nombre de service client possible',compute='_compute_available_service')
        nbr_service= fields.Integer(string='Nombre de service client', requiere=True , default=1, help='Nombre de service client que le service fournisseur peut crÃ©er')
        state= fields.Selection([('draft','Brouillon'), 
                                ('en_creation_fournisseur','en création' ),
                                  ('active', 'activé'),
                                  ('expirer','Expiré' ),
                                  ('terminer','Terminé')], default="draft")
        
        service_fournisseur_tmpl_id= fields.Many2one('cloud.service.tmpl.fournisseur', help='le template fournisseur qui a configurer le service fournisseur')
        paramclient = fields.Text('paramètres client (json data)')
        
        retour_api_param_service = fields.Text('Retour d api fournisseur', help="retour des parametres fournisseur du service crÃ©er en webservice")
        launch_script_ids =fields.Many2many('launch.script', help='liste des script Ã  lancer aprÃ¨s la creation du service fournisseur' )
        log_state_script = fields.Text('log de retour des script de post traitement')
        service_fournisseur_management = fields.Reference(selection=[('service.fournisseur.management.bibind','Gestion de Service fournisseur Bibind')])
        

        @api.constrains( 'availaible_service')
        def _check_service_limit(self):
            if self.availaible_service <0:
                    raise Warning(_('No more available service for this service fournisseur .'))
       

        @api.depends('availaible_service', 'nbr_service', 'cloud_service_ids')
        def _compute_available_service(self):
            """ Determine service available, """
            if self.cloud_service_ids:
                nb_service_actual = len(self.cloud_service_ids)
                self.availaible_service= self.nbr_service - nb_service_actual
            else :
                self.availaible_service = self.nbr_service
                
       

        def _get_fournisseur(self):
            if not self.fournisseur:
                tpml = self.service_fournisseur_tmpl_id
                self.fournisseur = tpml.fournisseur
                return self.fournisseur
            else:
                return self.fournisseur
        

        def _set_type_service(self):
             
            tpml = self.service_fournisseur_tmpl_id
            self.type_service = tpml.type_service
            
            return self.type_service
        
        
        def _set_launch_scripts(self):
             
            tpml = self.service_fournisseur_tmpl_id
            self.launch_script_ids = tpml.param_ids
            
            return self.launch_script_ids
        
        
        
        def create_fournisseur_host(self, host):
            
            model_host = self.env['cloud.service.host']
            vals ={
               
                'nodeid': host.id,
                'host_ipv4':host.public_ips,
                'hostip_v6':host.public_ips,
                'name':host.name,
                'hostname':host.name,
               
                
                
                }
            fournisseur_host = model_host.create(vals)
            return fournisseur_host.id
        
        
        

        def deploy_node(self):
            if not self.fournisseur:
                war = { 'warning': {'title': 'fournisseur', 'message':'Veuillez selectionner un fournisseur'} }
                return war
            if not self.fournisseur_api:
                res = { 'warning': {'title': 'Api fournisseur', 'message':'Veuillez selectionner une api du fournisseur'} }
                return res
            api = self._get_api_fournisseur()
            
            for host in self.host_ids:
                try:
                    hostid = self.env['bibind.host'].browse(host.id)
                    bibindnode = api.deploy_host(self, host)
                    if(bibindnode):
                        hostid.write({'nodeid':bibindnode.id, 'log':'ok'})
                    else :
                        hostid.write({'log':'probleme de node'})
                        
                except (IOError, OSError): 
                    res = { 'warning': {'title': 'Leve exception', 'message':'probleme de creation des nodes'} }
                    return res
            
            return True
        
        

        def deploy_script(self):
            if not self.fournisseur:
                war = { 'warning': {'title': 'fournisseur', 'message':'Veuillez selectionner un fournisseur'} }
                return war
            if not self.fournisseur_api:
                res = { 'warning': {'title': 'Api fournisseur', 'message':'Veuillez selectionner une api du fournisseur'} }
                return res
            api = self._get_api_fournisseur()
            
            if not self.host_ids:
                res = { 'warning': {'title': 'Host', 'message':'Veuillez selectionner ou creer des serveurs host'} }
                return res
            
            for host in self.host_ids:
                try:
                    hostid = self.env['bibind.host'].browse(host.id)
                    bibindnode = api.deploy_script(self, host)
                    if(bibindnode):
                        hostid.write({'nodeid':bibindnode.id, 'log':'ok'})
                    else :
                        hostid.write({'log':'probleme de node'})
                        
                except (IOError, OSError): 
                    res = { 'warning': {'title': 'Leve exception', 'message':'probleme de creation des nodes'} }
                    return res
            
            return True
        
        

        def deploy_specific_script(self):
            if not self.fournisseur:
                war = { 'warning': {'title': 'fournisseur', 'message':'Veuillez selectionner un fournisseur'} }
                return war
            if not self.fournisseur_api:
                res = { 'warning': {'title': 'Api fournisseur', 'message':'Veuillez selectionner une api du fournisseur'} }
                return res
            api = self._get_api_fournisseur()
            
            if not self.host_ids:
                res = { 'warning': {'title': 'Host', 'message':'Veuillez selectionner ou creer des serveurs host'} }
                return res
            
            for host in self.host_ids:
                if not host.deployed:
                    try:
                        hostid = self.env['bibind.host'].browse(host.id)
                        bibindnode = api.deploy_script(self, host)
                        if(bibindnode):
                            hostid.write({'nodeid':bibindnode.id, 'log':'ok'})
                        else :
                            hostid.write({'log':'probleme de node'})
                            
                    except (IOError, OSError): 
                        res = { 'warning': {'title': 'Leve exception', 'message':'probleme de creation des nodes'} }
                        return res
            
            return True
                        
            
                
            
            
        

        def run_service(self):
             
            if not self.fournisseur:
                war = { 'warning': {'title': 'fournisseur', 'message':'Veuillez selectionner un fournisseur'} }
                return war
            if not self.fournisseur_api:
                res = { 'warning': {'title': 'Api fournisseur', 'message':'Veuillez selectionner une api du fournisseur'} }
                return res
            api = self._get_api_fournisseur()
            
            #Pour chaque host on list les scripts de deploiement dans un tableau
            #si la node n'est pas déja crere On créer la node avec un deployeemnt du scrip
            #sinon on lance seulement script de deploiement
            
            
            try :
                host = api.create_host(self) 
                id = self.create_fournisseur_host(host)
                if id:
                    self.state='active';
                    return True
                else:
                    self.state='en_creation_fournisseur'
            except (IOError, OSError): 
                return False
                
        
        def _get_api_fournisseur(self):
            
            if not self.fournisseur_api:
                if not self.service_fournisseur_tmpl_id:
                    raise ValueError('Vous devez définir une api fournisseur: Soit par le template forunisseur ou directement par le service fournisseur')
                else :
                    tpml_id = self.service_fournisseur_tmpl_id.id
                    tmpl = self.env['cloud.service.tmpl.fournisseur'].browse(tpml_id)
                    
                    fournisseur_api_id = tpml.fournisseur_api.id
                    api = self.env['cloud.service.api.fournisseur'].browse(fournisseur_api_id)
                   
                    
                    self.write({'fournisseur_api', fournisseur_api})
                    
                    return api.ref_api
            else:
                    api = self.env['cloud.service.api.fournisseur'].browse(self.fournisseur_api.id)
                    return api.ref_api
        
        def _get_requete_api(self):
            
            tpml = self.service_fournisseur_tmpl_id
            requete_api_service = self.env['cloud.service.api.url.requete'].browse(tpml.requete_api_service.id)
            
            return requete_api_service
        
        def _get_requet_param_api(self):
             
             tpml = self.service_fournisseur_tmpl_id
             requete_param_api = self.env['cloud.service.requete.param'].browse(tmpl.param_api_requete)
             return requete_param_api
        
        
        
        
        def assigne_service_management(self):
            
            
            fournisseur = self._get_fournisseur()
            type_service = self.type_service
            api_fournisseur = self._get_api_fournisseur()
            service_management_id = api_fournisseur.api_ref.get_service_management(type_service)
            
            self.service_fournisseur_management = service_management_id
            
            return self.service_fournisseur_management
        
        
        
        def call_fournisseur_commande_service_create(self, param):
            
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            
            res = api.callcreateservice(self.type_service,url, requete_param_api, paramclient, self )
            if res:
                self.retour_api_param_service = json.dumps(res)
                self.state ='en_creation_fournisseur'
                return True
            else :
                self.state ='aucune_reponse'
                return False
            
        def call_get_order(self):
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            retour_api_param_service = json.load(self.retour_api_param_service)
            
            data_order = api.call_get_order(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
            if data_order:
                
                self.is_paid = True
                self.state = 'commande_creer'
                return data_order
            else :
                self.is_paid = False
                return False
            
        def call_get_invoice(self):
                apif = self._get_api_fournisseur()
                api = apif.ref_api
                url =self._get_requete_api()
                paramclient = self.paramclient
                requete_param_api = self._get_requet_param_api()
                retour_api_param_service = json.load(self.retour_api_param_service)
                
                data_order = api.call_get_invoice(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
                if data_order:
                    
                    self.is_paid = True
                    self.state = 'invoice_fournisseur'
                    return data_order
                else :
                    self.is_paid = False
                    return False
            
        def call_check_status_service(self):
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            if self.retour_api_param_service:
                retour_api_param_service = self.retour_api_param_service
            else:
                retour_api_param_service = {}
            res = api.call_check_statut_service(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
            if res:
                self.retour_api_param_service = res
                self.state ='active'
                
                return True
                
            return True
        
        
        def call_get_param_host(self):
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            if self.retour_api_param_service:
                retour_api_param_service = self.retour_api_param_service
            else:
                retour_api_param_service = {}
            param_host = api.call_get_param_host(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
            val = {}
            if param_host['host']:
                val= {
                       'ser_fourni_id': self.id,
                       'name':self.name +'-param host', 
                       'param_json_data':json.dumps(param_host), 
                       'host_ipv4':param_host['ipv4'],
                       'host_ipv6':param_host['ipv6'],
                       'hostname':param_host['hostname'],
                       'user_name':param_host['user'], 
                       'host_path':param_host['root_path'],
                       'password': param_host['password'],
                       
                      }
                if param_host['db_host']:
                    val.update({
                                'db_host': param_host['db_host'],
                               'db_name': param_host['db_name'],
                               'db_user':param_host['db_user'],
                               'db_password':param_host['db_pass'],
                                })
                self.param_host_state = param_host['status']
                param_host_ids =self.env['cloud.service.host.param'].create(val)
                self.param_host_ids = param_host_ids
                self.state ='parametre_host'
                return self.param_host_ids
            else :
                self.param_host_state = 'en_attente'
                return False
            
        
        def update_param_host(self, id_param_host):
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            if self.retour_api_param_service:
                retour_api_param_service = self.retour_api_param_service
            else:
                retour_api_param_service = {}
            param_host = api.call_update_param_host(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
            val = {}
            if param_host['host']:
                val= {
                      'ser_fourni_id': self.id,
                       'name':self.name +'-param host', 
                       'param_json_data':json.dumps(param_host), 
                       'host_ipv4':param_host['ipv4'],
                       'host_ipv6':param_host['ipv6'],
                       'hostname':param_host['hostname'],
                       'user_name':param_host['user'], 
                       'host_path':param_host['root_path'],
                       'password': param_host['password'],
                       
                      }
                if param_host['db_host']:
                    val.update({
                                'db_host': param_host['db_host'],
                               'db_name': param_host['db_name'],
                               'db_user':param_host['db_user'],
                               'db_password':param_host['db_pass'],
                                })
                param_host_id =self.env['cloud.service.host.param'].browse(id_param_host)
                param_host_id.write(val)
                return param_host_id
        
        
        def add_param_host_service(self):
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            if self.retour_api_param_service:
                retour_api_param_service = self.retour_api_param_service
            else:
                retour_api_param_service = {}
            param_host = api.call_add_param_host(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
            val = {}
            if param_host['host']:
                val= {
                       'ser_fourni_id': self.id,
                       'name':self.name +'-param host', 
                       'param_json_data':json.dumps(param_host), 
                       'host_ipv4':param_host['ipv4'],
                       'host_ipv6':param_host['ipv6'],
                       'hostname':param_host['hostname'],
                       'user_name':param_host['user'], 
                       'host_path':param_host['root_path'],
                       'password': param_host['password'],
                       
                      }
                if param_host['db_host']:
                    val.update({
                                'db_host': param_host['db_host'],
                               'db_name': param_host['db_name'],
                               'db_user':param_host['db_user'],
                               'db_password':param_host['db_pass'],
                                })
                
                param_host_id =self.env['cloud.service.host.param'].create(val)
                return param_host_id
            else :
                self.param_host_state = 'en_attente'
                return False
            return param_host
        

        def launch_scripts_configuration_service(self):
            self.state ='en_attente_post_traitement'
            
            if self.param_host_state == 'en_attente':
                return False
            
            if self.param_host_ids:
                param_host = self.param_host_ids
            else :
                param_host = self.call_get_param_host()
                
            if self.launch_script_ids:
                list_scripts = self.launch_script_ids
            else :
                list_scripts = self._set_launch_scripts()
            res ={}
            for script in list_scripts:
                script._prepare_param(param_host)
                succes = script.run()
                res.append(succes)
            
            self.log_state_script = json.dump(res)
            if all(item == True for item in res):
                self.state ="active"
            else:
                if any(item ==True for item in res):
                    self.state ="en_attente_post_traitement"
                else :
                    self.state ="en_attente_post_traitement"   
       
        def configure_service_client(self, objet_service_id) :
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            if self.retour_api_param_service:
                retour_api_param_service = self.retour_api_param_service
            else:
                retour_api_param_service = {}
            param_host_service = api.call_configure_service_and_add_param_host(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service,objet_service_id, self )
            val = {}
            if param_host_service:
                return param_host_service
            else:
                return False
        
        def get_date_expired(self) :
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            retour_api_param_service = self.retour_api_param_service
            res = api.call_get_date_expiration(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
            if res:
                self.expired = res['date']
            
        
        
        def update_date_expired(self, param):
            
            self.expired = param['date']
            return True
            
        
        def renew(self) :
            apif = self._get_api_fournisseur()
            api = apif.ref_api
            url =self._get_requete_api()
            paramclient = self.paramclient
            requete_param_api = self._get_requet_param_api()
            retour_api_param_service = self.retour_api_param_service
            res = api.call_renew_service(self.type_service,url, requete_param_api,  paramclient, retour_api_param_service, self )
            if res:
                self.update_date_expired(res)
                return True
            return False
            
        def check_number_service(self, cr, uid, ids) :
            # returns 
            return
                
        def prepare_service(self, cr, uid, ids) :
            """ prepare les donnÃ©e necÃ©ssaire pour la creation de service """
            # returns 
            return
        
        
        
        @api.model
        def create(self, vals) :
            # returns 
            context = self.env.context
            if vals.get('cloud_service_ids') and vals.get('nbr_service'):
                count = len(vals.get('cloud_service_ids'))
                if count > vals.get('nbr_service'):
                    raise osv.except_osv(_('Warning!'), _('Limit to create %s Lines' %(vals.get('nbr_service'))))

            if context is None:
                context = {}
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('cloud.service.fournisseur') or '/'
          
            new_id = super(Cloud_Service_fournisseur, self).create( vals)
            
            return new_id
        
        
        
            

Cloud_Service_fournisseur()



class cloud_service_tmpl_fournisseur(models.Model):
        _name = 'cloud.service.tmpl.fournisseur'
   
        state= fields.Selection(selection=[('draft', 'draft'), ('inprogress', 'inprogress'), ('configurer', 'template configurer')])
       
        name= fields.Char(string='nom du Template', size=128, required=True)
        
        fournisseur_id= fields.Many2one('res.partner', string="Fournisseur", required=True)
        
        product_id = fields.Many2one('product.product', 'produit liÃ© au service fournisseur')
        
        service_fournisseur_type = fields.Many2one('cloud.service.fournisseur.type', 'Type de service fournisseur')
        
        #service_fournisseur_id= fields.Many2one('cloud.service.fournisseur', 'template liÃ© Ã  un service fournisseur dÃ©jÃ  existant')
        
        api_fournisseur= fields.Many2one('cloud.service.api.fournisseur',string='Service api fournisseur',required=True, help='Choisir l api du fournisseur qui va crÃ©er le service fournisseur' )
        
        requete_api_service= fields.Many2one('cloud.service.api.url.requete',  string='Requete api creation service',required=True, help='choisisez une requete de service')
        
        param_api_requete= fields.One2many('cloud.service.requete.param', 'tmpl_fournisseur_id')
        
        #tmpl_service_fournisseur_depend= fields.Many2one('cloud.service.tmpl.fournisseur', requier=True, help='DÃ©pendance avec un autre template service fournisseur (creation du service fournisseur avant que celui ci puisse Ãªtre crÃ©er)')
        
        #Price= fields.Char('Prix du service fournisseur', size=128)
        
        nbr_service_client= fields.Integer(string='Nombre de service client', requiere=True , default=1, help='Nombre de service client que le service fournisseur peut crÃ©er')
        
        type_service = fields.Selection(selection=([
                                                    ('domain', 'Service domain'),
                                                    ('mutualise','Service Mutualisé'),
                                                    ('dedie_mutualise','Service Déidé Mutualisé'),
                                                    ('vm_mutualise','Service Virtual Machine pour Mutualisé'),
                                                    ('dedie','Service Serveur dédié'),
                                                    ('vm','Service Machine virtuel'),
                                                    ('infrastructure','Service infrastructure'),
                                                    ]))
        
        categorie_fournisseur_ids= fields.Many2one('cloud.service.categorie.fournisseur', string='categorie du service fournisseur', help='la catÃ©gorie  Ã  la quelle le service fournisseur va appartenir')
        
        param_ids = fields.Many2many('launch.script','ctsf_claunchscript', 'tmpl_fournisseur', 'launch_script' )
        
       # @api.one
        #@api.depends('invoice_line.price_subtotal', 'tax_line.amount')
        #def _compute_amount(self):
            #self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
            #self.amount_tax = sum(line.amount for line in self.tax_line)
            #self.amount_total = self.amount_untaxed + self.amount_tax
        
        #@api.one
        @api.depends('fournisseur_id')
        def _compute_selection_api_url(self):
          return True
            
        #@api.multi
        #@api.depends('fournisseur_id')
        def compute_requete_api_selection(self) :
            
            return
        
        def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if not partner_id:
                return {'domain': { }}
          
            return {
                'domain': {
                      'api_fournisseur': [('res_partner_id', 'in', [partner_id])],
             } }
        
        @api.onchange('api_fournisseur','requete_api_service')   
        def onchange_api_fournisseur_id(self):
            
          return
        
        @api.onchange('requete_api_service')
        def onchange_requete_api_service(self):
            
            return
        
        
        

        def config_url_param(self):
            if not self.requete_api_service:
                    res = {'warning': {
                        'title': _('Warning'),
                        'message': _('My warning message.')
                                }}
                    _logger.info('res %s' % (res))
                       
                    return res
            return True      
           
                
    
cloud_service_tmpl_fournisseur()
