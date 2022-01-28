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

from random import *
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
sys.path.insert(0, "/mnt/extra-addons/bibind/models/bibind_container")
from libcloud.compute.types import Provider
from libcloud.compute.providers import DRIVERS
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment, SSHKeyDeployment
from libcloud.compute.providers import set_driver
from libcloud_bibind.bibindrancher import BibindRancherContainerDriver

from libcloud.dns.types import Provider, RecordType
from libcloud.dns.types import RecordError
from libcloud.dns.types import ZoneDoesNotExistError, RecordDoesNotExistError
from libcloud.dns.base import DNSDriver, Zone, Record

from libcloud.dns.providers import get_driver as get_dns_driver
from libcloud.dns.providers import DRIVERS as DNSDRIVER 
import gitlab





_logger = logging.getLogger("bibind_cloudservice")


def generator_password():
    characters = string.ascii_letters + string.punctuation  + string.digits
    password =  "".join(choice(characters) for x in range(randint(8, 16)))
    return password



class bibind_api_dns(models.Model ):
    _name = 'bibind.api.dns'
    
    _inherit = 'bibind.zone.driver'
    
    name= fields.Char('nom', size=255)
    description= fields.Char('description', size=255)
   
    driver_cloud = fields.Many2one('cloud.service.nodedriver')
    
    def run_driver(self):
        
        driver_run_driver = 'run_driver'+self.driver_cloud.name
        fct = getattr(self._name , driver_run_driver)
        bibind_user_id = self.env.user.bibind_user_id        
        medrive = self.env['bibind.me.drivers'].search([('driver','=',self.driver_cloud.name), ('bibind_user','=', bibind_user_id)])
               
        if isinstance(bfct, types.FunctionType):
                driver =fct(medrive)
                return driver
        else :
            raise Warning(_('Aucune methode implementer pour ce driver .'))
   
    def run_driver_ovh(self, medriver):
        
                Driver = get_driver(Provider.OVH)
                
                driver = Driver(medriver.ovh_applicationkey, medriver.ovh_secretkey, medriver.ovh_projetid, medriver.ovh_consumerkey)
                
                return driver
    
    def run_driver_rancher(self, medriver):
                set_driver('bibindrancher',
                   'libcloud_bibind.bibindrancher',
                   'BibindRancherContainerDriver')

                Driver = get_driver(Provider.RANCHER)
                
                driver = Driver(medriver.rancher_accesskey, medriver.rancher_secretkey, medriver.rancher_url, medriver.rancher_port, medrive.rancher_secure)
                rancher_port
                return driver
        
    
bibind_api_dns()





