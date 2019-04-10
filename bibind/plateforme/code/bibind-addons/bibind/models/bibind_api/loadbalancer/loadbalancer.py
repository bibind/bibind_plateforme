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
from openerp.osv import fields, osv
from openerp import pooler, tools
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
from openerp import models, fields, api, _
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
from libcloud.loadbalancer.base import Driver 
from libcloud.loadbalancer.types import Provider
from libcloud.loadbalancer.providers import DRIVERS
from libcloud.loadbalancer.providers import get_driver
from libcloud.loadbalancer.providers import set_driver

from PIL.EpsImagePlugin import field


class bibind_loadbalancer(models.Model):
        _name ="bibind.loadbalancer"
        _description="load balancer"
        
        def _get_state_lb(self):
            
            st=[
                ('RUNNING', 'running'),
                ('PENDING' , 'pending'),
                ('UNKNOWN' , 'unknown'),
                ('ERROR' , 'error'),
                ('DELETED' , 'deleted')]
            
            return st
       
        lb_id = fields.Char('Id libcloud of the container')
        name = fields.Char('Name')
        ip = fields.Char('Id of the loadbalencer')
        state = fields.Selection(selection=_get_state_lb, string='State')
        port = fields.Integer( string='Port')
        driver = fields.Many2one('bibind.container.driver')
        extra = fields.Text('Extra')
        api_driver =fields.Reference(selection=[('cloud.service.api.bibind','bibind compute'), ('bibind.api.container', 'Bibind container')], string='api')
        
        
        def create_balancer(self, container):
            
            return balancer
        
           
        
        
bibind_loadbalancer()      
  
  

class bibind_balancer_driver(models.Model):
        _name = "bibind.balancer.driver"
        _description = "LoadBalancer driver class"
        
        
        def _get_provider_constante(self):
       
           pro = []
           for key  in DRIVERS: 
               pro.append((key,key))
           return pro
    
    
        name = fields.Char('name du driver')
        provider = fields.Selection(selection='_get_provider_constante')


bibind_container_driver()