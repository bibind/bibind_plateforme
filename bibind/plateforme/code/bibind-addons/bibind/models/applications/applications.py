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
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp import pooler, tools
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
from lxml import etree
import paramiko
from paramiko import SSHClient
from paramiko import SFTPClient
import ovh


import ansible.playbook
import ansible.inventory

from ansible import utils
import json


_logger = logging.getLogger("auguria_cloudmanager")

class cloud_service_application_category(models.Model):
        _name = 'bibind.application.category'
        _description = 'categories des applications'
        _order = 'sequence'


        
    
  
        name= fields.Char('Name', required=True, translate=True, select=True)
        description= fields.Char('Description')
        parent_id= fields.Many2one('bibind.application.category','Parent Category', select=True, ondelete='cascade')
        child_id= fields.One2many('bibind.application.category', 'parent_id', string='Child Categories')
        sequence= fields.Integer('Sequence', select=True, help="Gives the sequence order when displaying a list of application categories.")
        type= fields.Selection([('view','View'), ('normal','Normal')], 'Category Type', help="A category of the view type is a virtual category that can be used as the parent of another category to create a hierarchical structure.")
        parent_left= fields.Integer('Left Parent', select=1)
        parent_right= fields.Integer('Right Parent', select=1)
    

    
        _defaults = {
            'type' : 'normal',
        }
    
        
    
        _constraints = [
            (models.BaseModel._check_recursion, 'Error ! You cannot create recursive categories.', ['parent_id'])
        ] 
        
cloud_service_application_category()


class cloud_service_application(models.Model):
        _name = 'bibind.application'
        _description = 'application'
        _order = 'name'



        name= fields.Char(string="Nom de l'application")
        description= fields.Char(string="Description de l'application")
        depot_git = fields.Char(string="depot Git")
        version = fields.Char(string="version")
        category =fields.Many2one('bibind.application.category',string='Category')
        
       
        
       
       
        
        
    
cloud_service_application()

