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

from openerp.exceptions import Warning
from openerp import models, fields, api, _
from openerp import pooler, tools
from openerp.tools.translate import _
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
import json
import re
from lxml import etree
import paramiko
from paramiko import SSHClient

from socket import getaddrinfo
from pygments.lexer import _inherit
from sre_constants import BRANCH

_logger = logging.getLogger("bibind_cloudservice")

#rancher
#cle d acces :15885440FBC11F4B5520
#cle secret :ULG9SLfxijd9ei4TBhFu5SpdStyyMNtLWXGCr5mU


     
     
class bibind_service_delivery(models.Model):
     _name = 'bibind.service.delivery'
     _inherit = ['mail.thread', 'ir.needaction_mixin']
     _description = 'Bibind delivery'
     
    
     service_id = fields.Many2one('bibind.services', 'Service Info', required=True)
     odoo_user_id = fields.Many2one('res.users',  related='service_id.odoo_user_id', default=lambda self: self.env.user.id, required=True)
     odoo_partner_id = fields.Many2one('res.partner', related='service_id.odoo_partner_id', )
     bibind_user_id = fields.Many2one('bibind.user', 'Créateur du service', related='service_id.bibind_user_id',  )
     bibind_team_ids = fields.Many2many('bibind.user', related='service_id.bibind_team_ids')
     
     site_name = fields.Char('Nom du site Web', required=True)
     
     environnement = fields.One2many('bibind.continous.environnement', 'service_continous_id', string="Environnement")
     
     rancher_servicelb =fields.Many2one('bibind.container', string='LoadBalancer container')
     rancher_env_id = fields.Char('Environnement Rancher')
     rancher_stack_id = fields.Char('stack Rancher')
     
     application = fields.Many2one('bibind.application', 'Application')
     
    
     
     fournisseur_id = fields.Many2one('cloud.service.fournisseur', related='service_id.bibind_fournisseur', string='Fournisseur', required=True)
     
     hosts = fields.Many2many('bibind.host', related='fournisseur_id.host_ids')
     
     depot_id = fields.Many2one('bibind.depot', related='service_id.depot_id')
     
     depot_url = fields.Char(related='depot_id.ssh_url')
     
     depot_is_created = fields.Boolean(string="depot creer")
     
     projet_id = fields.Many2one('project.project', string='Projet lié au service')
     
     chose_driver = fields.Boolean(string='Choisir son provider', default=False)
     
     log = fields.Text('log')
     
     
     
     def populate_depot(self):
         
         
         depot = self.depot_id
         application = self.aplication
         depot.populate_depot(self, application, **kwargs)
         
         api.create_environnement_dev()
         
     def create_dev_environnement(self):
         
        if not self.aplication:
                    raise Warning(_('Vous devez choisir une application .'))
        if not self.depot_id:
                    raise Warning(_('Vous devez créer un depot .'))
        if not self.fournisseur_id:
                    raise Warning(_("Le provider est manquant"))
        
        
        if not any(self.env.user.id in u for u in self.bibind_team_ids) and self.env.user.id !=self.service_id.bibind_owner_user.id :
             raise Warning(_("Vous n'avez pas les permission pour creer un environnement"))
        
        user =self.bibind_user_id
       
        app = self.aplication
        partner_name = self.bibind_user_id.name
        depot_url = self.depot_url
        site_name = self.site_name
        env = self['bibind.continous.environnement']
        dev_env = env.create_environnement(stack)
        
        return dev_env
    
    
     @api.multi  
     def create_depot(self, depot_name=None):
        
        if depot_name==None:
            depot_name= self.site_name 
        if not self.depot_is_created:  
            depot = self.env['bibind.depot']
            import_url = self.application.depot_git
            depotid = depot.bibind_create_depot(self.bibind_user_id, self.site_name, import_url)
            if depotid:
                self.depot_id = depotid.id
                self.depot_is_created = True;
                return self.depot_id
            else:
                return False
     
     
     @api.multi  
     def get_api(self):
         
         return False
         
     
     
     
    
     @api.multi  
     def create_test_env(self):
         
         return env_id
     
     @api.multi  
     def create_live_env(self):
         
         return env_id
     
     
     @api.multi  
     def create_branche_env(self):
         
         return env_id
     @api.multi  
     def get_branch_env(self):
         
         return branch 
     
     @api.one
     @api.multi 
     def get_rancher_env_id(self):
         
         if not self.rancher_env_id:
            api = self.env.ref('bibind.bibind_api_container_rancher')
            env = api.get_rancher_environnement(self, 'dev')
            if env:
                self.rancher_env_id = env.id
                self.rancher_env_id = stack.projet_id
                return rancher_env_id
         
     
     @api.multi  
     def create_rancher_env_id(self):
         
         return rancher_env_id
     
     @api.multi  
     def create_stack(self):
         
       
         return rancher_stack_id
     
     
     @api.multi  
     def delete_stack(self):
         
        if self.rancher_env_id and self.rancher_stack_id:
            api = self.env.ref('bibind.bibind_api_container_rancher')
            delete = api.delete_rancher_stack(self.rancher_env_id, self.rancher_stack_id)
            if not delete:
                self.rancher_stack_id = ''
     
     
     @api.multi  
     def get_stack(self):
         
         return rancher_stack_id
     
     
     @api.multi  
     def deploy_dev_env(self):
         api = self.env.ref('bibind.bibind_api_container_rancher')
         stack = api.deploy_environnement(self, 'dev')
         if stack:
             self.log = stack
             self.rancher_stack_id =stack['id']
             
         return False
     
     
     @api.multi  
     def get_service_lb(self):
         
         return lb
     
     
     @api.multi  
     def update_lb(self):
         
         return lb
     
     
     @api.multi  
     def create_lb(self):
         
         return lb
     @api.multi  
     def deploy_dev_to_test(self):
         
         return True
     
     @api.multi  
     def deploy_test_to_live(self):
         
         
         return True
     @api.model
     def create(self, vals):
         
         delivery_id = super(bibind_service_delivery, self).create(vals)
         return delivery_id
     
     
            
     
     
     
bibind_service_delivery()
     
     
     
     
     

     
class continous_environnement(models.Model):
    
    _name = 'bibind.continous.environnement'



    type = fields.Selection(selection=[('Branche', 'Branche'),('live', 'Production'), ('test','Test'), ('dev','Developpement')], string="Type de l'environnement")
    
    
    branche = fields.Char('Branche du depot')
    service_continous_id = fields.Many2one('bibind.service.delivery', requered=True)
    depot = fields.Many2one('bibind.depot', related='service_continous_id.depot_id')
    depot_url = fields.Char('url du depot', related='depot.url')
    
    containerids = fields.Many2many('bibind.container', 'environnement_id')
    
    url_app = fields.Char(string="Url frontend de l'application")
    url_app_admin = fields.Char(string="Url backend de l'application")
    domain = fields.Many2many('bibind.service.domain',relation='delivery_domain',)
    domain_zone =fields.Many2one('bibind.zone', related='domain.zone_id')
    
    login_sftp = fields.Char('Login SFTP')
    password_sftp = fields.Char('password sftp')
    
    login_db = fields.Char('Login db')
    password_db = fields.Char('password db')
    databas_name = fields.Char('database name')
    
    login_admin_app = fields.Char('Login admin')
    password_admin_app = fields.Char('password admin')


   
    service_id = fields.Many2one('bibind.services', related='service_continous_id.service_id')
    service_fournisseur_id = fields.Many2one('cloud.service.fournisseur', related='service_continous_id.fournisseur_id')
    
    hosts = fields.Many2many('bibind.host', related='service_fournisseur_id.host_ids')
    
    rancher_env_id = fields.Char('Environnement Rancher')
    rancher_stack_id = fields.Char('Environnement Rancher')
    
    
    def is_test_env(self):
        if self.type=='test':
            return True
        else:
            return False
        
    def is_dev_env(self):
        if self.type=='dev':
            return True
        else:
            return False
    
    def is_live_env(self):
        if self.type=='live':
            return True
        else:
            return False
        
    def is_branch_env(self):
        if self.type=='Branche':
            return True
        else:
            return False
        
    def _get_branche(self):
        
        return self.branche
    
    def create_environnement(self , delivery, env, type='dev', branche='developpement'):
        
        vals = {}
        vals ={
            'type':type,
            'branch':branche,
            'depot':delivery.depot_id,
            'depot_url': delivery.depot_id.url,
            'host': todo,
            'login_sftp':todo,
            'password_sftp':todo,
            'service_continous_id':delivery.id,
            }
       
        
        envid = self.create(vals)
        model_container = self.env['bibind.container']
        containers = []
        for container in env.container:
             container_id = model_container.create_container(env_id, container)
             containers.append(container_id)
        
        env_id.write({'containerids':[(6, 0, containers)]})
            
        return env_id
    
    def deploy_environnement_dev(self):
        
        
   
        if not self.rancher_stack_id:
            api = self.env.ref('bibind.bibind_api_container_rancher')
            stack = api.deploy_environnement(self)
            self.rancher_stack_id = stack.id
            self.rancher_env_id = stack.projet_id
            
        model_container = self.env['bibind.container']
        containers = []
        for container in stack.containers:
             container_id = model_container.create_container(env_id, container)
             containers.append(container_id)
        
        env_id.write({'containerids':[(6, 0, containers)]})
            
        return env_id
        
        
        
        
    
   
continous_environnement()



