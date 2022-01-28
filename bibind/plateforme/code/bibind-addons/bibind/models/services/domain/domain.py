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

from odoo.exceptions import Warning
from odoo import models, fields, api, _

from odoo.tools.translate import _
from odoo.osv.expression import get_unaccent_wrapper
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import odoo.addons.decimal_precision as dp
from odoo import netsvc
import logging
import json
import re
from lxml import etree
import paramiko
from paramiko import SSHClient

from socket import getaddrinfo
from pygments.lexer import _inherit

_logger = logging.getLogger("bibind_cloudservice")



class bibind_service_domain(models.Model):
     _name = 'bibind.service.domain'
     _inherit = ['mail.thread','mail.activity.mixin']
     _description = 'Bibind domain'
     
     
     name = fields.Char('Nom de domain', requered=True)
     state = fields.Selection(selection=[
            ('draft', 'Domain brouillon'),
            ('valide', 'Domain disponible'),
            ('attente_register', 'Domain en attente du register'),
            
            ('done', 'Domain enregistré'),
            ], string='Status', readonly=True, copy=False, help="Gives the status of the domain.\
              .", select=True)
     
     zone_id = fields.Many2one('bibind.zone')
     
     #domain_record_ids = fields.Many2many('bibind.zone.record', 'zone', related='zone_id.records.')
     
     service_ids = fields.Many2one('bibind.services', requered=True)
     
     domain_nameserver= fields.One2many('bibind.domain.nameserver', 'service_domain_id',string="Serveur name")
     
     
     
     
     
     
     
     
     
class bibind_domain_nameserver(models.Model):

        _name = 'bibind.domain.nameserver'
        _description = 'domain nameserver'
        
        
        
        def onchange_status(self, cr, uid, ids, part, context=None):
        
            return True
        
        
        
        toDelete = fields.Boolean('A supprimer', default=False, required=True)
        host = fields.Char('Serveur DNS', size=256, required=True)
        isUsed = fields.Boolean('Status', default=False, required=True)
       
        ip = fields.Integer('IP associé', default=256, required=True)
        
        service_domain_id = fields.Many2one('bibind.service.domain',"Nom de domain" )
            
   
bibind_domain_nameserver()