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
from PIL.EpsImagePlugin import field

_logger = logging.getLogger("bibind_cloudservice")


class bibind_services(models.Model):
    _name ="bibind.services"
    _description ="Service cloud bibind (tous les services bibind)"
    
    
    
    name = fields.Char('Réference du service')
    display_name = fields.Char('Réference du service')
    created_date = fields.Datetime('Date de creation')
    expire_date = fields.Datetime("date d'expiration")
    termineted_date = fields.Datetime('Date de fin')
    last_update = fields.Datetime('Date de mise à jour')
    last_renew_date = fields.Datetime('Derniere date de renouvellement')
    state = fields.Selection(selection=[('draft', 'brouillon'), ('running', 'actif'), ('suspendu', 'suspendu'), ('termine', 'terminer')], default='draft')
    is_pay = fields.Boolean('payé')
    type_paiement = fields.Selection(selection=[('manual','manuelle'),('auto','automatique')])
    period_paiement = fields.Selection(selection=[('heure', 'par heure'), ('monthly','par mois'), ('yearly', 'par an')])
    
    
    service_instance_id =fields.Reference(selection=[('bibind.delivery.continous', 'Service de livraison continue')])
   
    odoo_user_id = fields.Many2one('res.users',  default=lambda self: self.env.user.id, required=True)
    odoo_partner_id = fields.Many2one('res.partner', related='odoo_user_id.partner_id', default=lambda self: self.env.user.partner_id)
   
    bibind_user_id = fields.Many2one('bibind.user', 'Créateur du service', default=lambda self: self.env.user.bibind_user_id, required=True)
    bibind_owner_user = fields.Many2one('bibind.user', 'Propriétaire du service',  default=lambda self: self.env.user.bibind_user_id)
    
    
    bibind_organisation =fields.Many2one('bibind.me.organisation', 'Societe proprietaire du service')
    
    bibind_admin_ids = fields.Many2many('bibind.user')
    bibind_techniques_ids = fields.Many2many('bibind.user')
    bibind_facturation_ids = fields.Many2many('bibind.user')
    bibind_team_ids = fields.Many2many('bibind.user')
    
    product_id = fields.Many2one('product.template', string="produits du service", required=True)
    
    bibind_fournisseur = fields.Many2one('cloud.service.fournisseur', string="Service fournisseur", required=True)
    depot_id = fields.Many2one('bibind.depot')
    depot_is_created = fields.Boolean('depot créer')
    
    
    
    
    def get_default_bibind_user(self):
        user = self.env.user.partner_id
        bibind_user = user.get_bibind_user
        
    
    def create_depot(self, depot_name=None):
        
        if depot_name==None:
            depot_name= self.name 
           
        depot = self.env['bibind.depot']
        depotid = depot.bibind_create_depot(self.bibind_user_id, depot_name, import_url)
        if depotid:
            self.depot_id = depotid.id
            self.depot_is_created = True;
            return self.depot_id
        else:
            return False
        
    def confirm_service(self):
        
        return True
        
    def create_product_service(self, site_name=None):
        product = self.product_id
        model = product.model_services
        instance = self.en[model]
        vals ={
            'service_id':self.id,
            'fournisseur_id':self.bibind_fournisseur,
            'hosts':self.bibind_fournisseur.host_ids,
            }
        
        instance.create(vals)
        
        return instance
        
    
    
    
bibind_services ()



class bibind_group(models.Model):
    _name = 'bibind.group'
    
    GROUP = [('administrateur', 'administrateur'), ('technique', 'developpeur'), ('facturation','Contact facturation' )]
    
    def _get_group(self):
        
        return GROUP
    
    name = fields.Char('Nom du membre')
    bibind_user_id = fields.Many2one('bibind.user', 'membre')
    group = fields.Selection(selection=_get_group)
    service_id = fields.Many2one('bibind.services', 'service qui est lié aux group')
    
    
    
    