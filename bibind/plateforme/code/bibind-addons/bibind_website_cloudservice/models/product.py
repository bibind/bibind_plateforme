# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-Today OpenERP SA (<http://www.openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import tools
from openerp.osv import osv, fields


class product_template(osv.Model):
    _inherit = ["product.template"]
    _name = 'product.template'
    _mail_post_access = 'read'

   
    _columns = {
        
       'cloudservice_is': fields.boolean('is cloudservice product', copy=False),
       'cloudservice_is_domain': fields.boolean('est-ce un nom de domain', copy=False),
       'template_service-fournisseur_id': fields.many2one('service.template.fournisseur','product_alternative_rel','src_id','dest_id', string='template service founisseur ', help=''),
        
        }


    _defaults = {
       
    }




class product_supplierinfo(osv.osv):
    _name = "product.supplierinfo"
    _description = "Information about a product supplier"



    _columns = {
        
         }