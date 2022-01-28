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
from odoo import models, fields, api, _
from odoo.tools.translate import _
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


_logger = logging.getLogger("dedaluvia_cloudservice")



class product_template(models.Model):
        _name = 'product.template'
        _inherit = ["product.template"]
        

        cloud_service_tmpl_id = fields.Many2one('cloud.service.tmpl', string='Template de service', help='lie le produit  un template service pour sa creation lors de la livraison client')
        product_depend_id = fields.Many2one('product.template', 'dependance avec un autre produit')
        is_cloud_service_product = fields.Boolean('Cloud service product', default=False)
        is_domain_product =fields.Boolean('Est-ce un service de type domain', default=False)
        
        model_services = fields.Selection(selection=[('bibind.service.delivery.continous', 'Delivery continous')])
        
        
        def onchange_api(self,cr, uid, ids, is_cloud_service_product):
            
            return True
        
        
        
product_template()

class product_supplierInfo(models.Model):
        _name = 'product.supplierinfo'
        _inherit = 'product.supplierinfo'
        
        
        cloud_service_fournisseur_tmpl_id = fields.Many2one('cloud.service.tmpl.fournisseur', help='lie les info du produit fournisseur  un template de fournisseur qui permettra la creation du service fournisseur lors de la livraison du fournisseur ')
        
        
        def change_price_suplier(self, cr, uid, ids) :
            # returns 
            return
    
product_supplierInfo()

