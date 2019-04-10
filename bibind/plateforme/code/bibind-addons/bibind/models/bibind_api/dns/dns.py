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


from libcloud.dns.providers import get_driver as get_dns_driver
from libcloud.dns.providers import DRIVERS as DNSDRIVER 
from libcloud.dns.types import Provider, RecordType
from libcloud.dns.types import RecordError
from libcloud.dns.types import ZoneDoesNotExistError, RecordDoesNotExistError
from libcloud.dns.base import DNSDriver, Zone, Record


from PIL.EpsImagePlugin import field


class bibind_zones(models.Model):
        _name ="bibind.zone"
        _description="Zone dns"
        
        
        
        def list_record_types(self):
            """
            Return a list of RecordType objects supported by the provider.
    
            :return: ``list`` of :class:`RecordType`
            """
            return list(self.RECORD_TYPE_MAP.keys())
    
    
        
    
        
        zone_id = fields.Char('Id de la zone')
        domain = fields.Char('Domain')
        type = fields.Selection(selection='list_record_types' , string='Record type')
        ttl = fields.Integer(string='Default TTL for records in this zone (in seconds')
        records = fields.One2many('bibind.zone.record','zone')
        driver = fields.Many2one('bibind.zone.driver')
        api_driver =fields.Reference(selection=[('bibind.api.dns','bibind dns')], string='api')
        extra = fields.Text('Extra')
        
        def create_container(self, environnement, container):
            
            return container
        
           
        
        
bibind_zones()      
  
  
class bibind_zone_record(models.Model):
        _name = "bibind.zone.record"
        _description = "Record in zone"
        
        
        
        
        
        zone_record_id = fields.Char('Id libcloud of the image')
        name = fields.Char("Name")
        type = fields.Char(string="DNS record type (A, AAAA, ...)")
        data = fields.Char(string="Data for the record (depends on the record type)'Path of the image'")
        zone = fields.Many2one('bibind.zone', string="Zone instance")
        driver = fields.Many2one('bibind.zone.driver')
        ttl = fields.Char('Record TTL')
        extra = fields.Text('Extra')
        api_driver =fields.Reference(selection=[('bibind.api.dns','bibind dns')], string='api')
       
        
        
        


bibind_zone_record()     
        
        
class bibind_zone_driver(models.Model):
        _name = "bibind.zone.driver"
        _description = "A cluster group for containers"
        
        def _get_provider_constante(self):
       
           pro = []
           for key  in DNSDRIVER: 
               pro.append((key,key))
           return pro
    
    
        name = fields.Char('name du driver')
        provider = fields.Selection(selection='_get_provider_constante')

        
bibind_zone_driver()       
        

        
