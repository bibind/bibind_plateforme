## -*- encoding: utf-8 -*-
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

from odoo import models, fields, api, _
from odoo import tools
from odoo.tools.translate import _
from odoo.osv.expression import get_unaccent_wrapper

from odoo import netsvc
import logging
import json
import re
from lxml import etree
import paramiko
from paramiko import SSHClient
import ovh
import requests
import sys
from libcloud.compute.types import Provider
from libcloud.compute.providers import DRIVERS
from libcloud.compute.providers import get_driver
import gitlab

_logger = logging.getLogger("bibind_cloudservice")




class bibind_me(models.Model):
    _name ='bibind.user'
    
    
    
    name =fields.Char(string='name', related='partner_id.name')
    odoo_user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string=' user ', default=lambda self: self.env.user.partner_id)
    
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', size=24, change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", 'State', ondelete='restrict')
    country_id= fields.Many2one('res.country', 'Country', ondelete='restrict')
    email = fields.Char('Email', related='partner_id.email')
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')
    mobile = fields.Char('Mobile')
    birthdate = fields.Char('Birthdate')
    
    gitlab_id = fields.Char('Id gitlab')
    gitlab_username = fields.Char('gitlab username')
    
    @api.model
    def open_bibind_me(self):
        
        _logger.info('+debutt %s  ' %('tttt') )   
        user = self.env.user.partner_id
        bibindme = self.env['bibind.me'].search([('partner_id','=', user.id)])
        
        _logger.info('+after bibindme %s  ' %(bibindme) )  
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bibind.me',
            'res_id': bibindme.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }
     

    def get_gitlab_id(self):
         gl = gitlab.Gitlab('https://lab.bibind.com/', '3Kb2LjfCW-Qn1RLyTP2y', ssl_verify=False)
         gl.auth()
         
         user = gl.users.list(username='root')[0]
         _logger.info('+debutt %s  ' %(user) )   
         
         if user:
             self.gitlab_id = user.id
             self.gitlab_username = user.username
             return True
         
    @api.model   
    def create_gitlab_id(self):
        if not self.gitlab_id and 1==2:
             gl = gitlab.Gitlab('https://lab.bibind.com/', '3Kb2LjfCW-Qn1RLyTP2y', ssl_verify=False)
             gl.auth()
             user_data = {'email': self.partner_id.email,  'username': self.name, 'name': self.name,  'password': 'testetstets44',}
             gitlab_user = gl.users.create(user_data)
             
             if user:
                 self.gitlab_id = user.id
                 self.gitlab_username = user.username
                 return True
        else:
            return True
        
        
    
    
    
class bibind_me_organisation(models.Model):
    _name ='bibind.me.organisation'
    
    
    def _default_bibind_me(self):
        _logger.info('+debutt default %s  ' %('tttt') ) 
        user = self.env.user.partner_id
        bibindme = self.env['bibind.user'].search([('partner_id','=', user.id)])
        _logger.info('+bibindme %s  ' %(bibindme) )        
        return bibindme.id
    
    
    name =fields.Char(string='name')
   
    bibind_me_id = fields.Many2one('bibind.user', ' user ', default=_default_bibind_me)
    organization = fields.Char('name')
    
    
    @api.model
    def open_bibind_me_organtisation(self):
        _logger.info('+organisation utt %s  ' %('tttt') )   
        user = self.env.user.partner_id
        bibindme = self.env['bibind.user'].search([('partner_id','=', user.id)])
        organisationme = self.env['bibind.me.organisation'].search([('bibind_me_id','=', bibindme.id)])
        
        if organisationme:
              
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'bibind.me.organisation',
                'res_id': organisationme.id,
                'view_mode': 'form',
                'view_type': 'form',
                'view_id':'bibind_organisation_form',
                'target': 'current',
            }
        else :
            wizard_form = self.env.ref('bibind.bibind_organisation_create_form', False)
            _logger.info('+debutt %s  ' %(wizard_form) ) 
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'bibind.me.organisation',
                'view_mode': 'form',
                
                'view_type': 'form',
                'view_id':wizard_form.id,
                'context':{'org_partner_id':bibindme.id},
                'target': 'current',
            }
        
    
    
class bibind_me_drivers_authentification(models.Model):
    _name ='bibind.me.drivers'
    
    def _get_provider_constante(self):
       
           pro = []
           for key  in DRIVERS: 
               pro.append((key,key))
           return pro
    
    name = fields.Char(string='name')
    drivers = fields.Selection(selection='_get_provider_constante')
    bibind_user = fields.Many2one('bibind.user')
    partner_id = fields.Many2one('res.partner', string=' user ', related='bibind_user.partner_id')
   
 
bibind_me_drivers_authentification()



class bibind_me_drivers_ovh_authentification(models.Model):
    
    _inherit ='bibind.me.drivers'
    
    def _get_location(self):
        location = [
            ('SBG1','Strasbourg 1'),
            ('BHS1', 'Montreal 1'),
            ('GRA1', 'Gravelines 1'),
            ]
        return location

    def _get_entpoint(self):
        
        
           pro = []
           for key  in ovh.client.ENDPOINTS  : 
               pro.append((key,key))
           return pro 
    
    
   
    ovh_location = fields.Selection(selection='_get_location', string='Location')
    ovh_endpoint = fields.Selection(selection='_get_entpoint',string='endpoint',help='choisir lendpoint' )
    ovh_applicationkey =fields.Char('applicationkey')
    ovh_secretkey = fields.Char('secret key')
    ovh_consumerkey = fields.Char('Consumer key')
    ovh_projetid = fields.Char('projet Id')
 
bibind_me_drivers_ovh_authentification()



class bibind_me_drivers_rancher_authentification(models.Model):
    
    _inherit ='bibind.me.drivers'
     
    rancher_accesskey = fields.Char('access key')
    rancher_secretkey = fields.Char('secret key')
    rancher_url = fields.Char('url of rancher')
    rancher_port = fields.Integer('Port')
    rancher_secure = fields.Boolean('Securite')
 
bibind_me_drivers_ovh_authentification()
    
    
class res_partner(models.Model):
    
    _inherit = 'res.partner'
    
    
    def _get_provider_constante(self):
       
       pro = []
       for key  in DRIVERS: 
           pro.append((key,key))
       return pro
    
    is_cloud_fournisseur = fields.Boolean(string='cloudsupplier', select=True, copy=True,
                                 help="Cocher si ce fournisseur a une api")
                
    libcloudcst = fields.Char('Constante libcloud', size=255 )
    libcloudselection = fields.Selection(selection='_get_provider_constante', string='Provider name')
    api_ids = fields.One2many('cloud.service.api.fournisseur','res_partner_id' )
    
    
    
    @api.onchange('libcloudselection')
    def _libcloud_constante(self):
        if self.libcloudselection!=False:
            self.libcloudcst = self.libcloudselection
        
                
                


    def onchange_api(self, is_company):
       
        return True
    
class res_users(models.Model):
    
    _inherit = 'res.users'
    
    username = fields.Char('username')
    bibind_user_id = fields.One2many('bibind.user', 'odoo_user_id', string='Bibind user associé', limit=1)
    gitlab_user_id = fields.Char(string="gitlab id", related='bibind_user_id.gitlab_id')
   
    
    
    
    
    @api.model
    def create(self, vals):
        
         _logger.info('+user before %s  ' %(vals) ) 
         user = super(res_users, self).create( vals)
         _logger.info('+user  %s  ' %(user) ) 
         _logger.info('+user name %s  ' %(user.name) ) 
         _logger.info('+user name %s  ' %(user.login) ) 
         _logger.info('+user id %s  ' %(user.id) ) 
         if user.login!='bibindtemplate':
             _logger.info('+user gitlab  before %s  ' %(vals) ) 
             groupbibinduser = self.env['res.users'].browse(user.id).has_group('bibind.group_user')
             if groupbibinduser and user.login!='bibindtemplate':
                gitlab = self.env['bibind.api.gitlab']
                _logger.info('+user after admin before %s  ' %(vals) ) 
                gitlab_user = gitlab.create_user(user, vals)            
                _logger.info('+gitlab_user %s  ' %(gitlab_user) )  
                if user:
                    value ={}
                    bibind_user = self.env['bibind.user']
                    values = {
                      'name':user.name,
                         'odoo_user_id':user.id,
                         'partner_id':user.partner_id.id,
                         'email':user.email,
                         }   
                         
                    if gitlab_user:
                        values.update({
                             'gitlab_id' : gitlab_user.id,
                             'gitlab_username' : gitlab_user.username,
                             })   
                        bibind_user_id = bibind_user.create(values)
                        
                        return user
                else :
                    return user
             else:
                 return user  