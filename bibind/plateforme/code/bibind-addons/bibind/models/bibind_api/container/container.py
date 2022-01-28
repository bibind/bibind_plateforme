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
import libcloud
from libcloud.container.base import ContainerDriver
from libcloud.container.types import Provider
from libcloud.container.providers import DRIVERS
from libcloud.compute.providers import get_driver
from libcloud.compute.providers import set_driver

from PIL.EpsImagePlugin import field


class bibind_container(models.Model):
        _name ="bibind.container"
        _description="Container"
        
        def _get_state_container(self):
            st=[
                ('RUNNING', 'running'),
                ('REBOOTING' , 'rebooting'),
                ('TERMINATED' , 'terminated'),
                ('PENDING' , 'pending'),
                ('UNKNOWN' , 'unknown'),
                ('STOPPED' , 'stopped'),
                ('SUSPENDED' , 'suspended'),
                ('ERROR' , 'error'),
                ('PAUSED' , 'paused')]
            
            return st
        
        container_id = fields.Char('Id libcloud of the container')
        name = fields.Char('Name')
        image = fields.Many2one('bibind.container.image')
        state = fields.Selection(selection=_get_state_container, string='State')
        ip_addresses = fields.Char('List address')
        driver = fields.Many2one('bibind.container.driver')
        api_driver =fields.Reference(selection=[('cloud.service.api.bibind','bibind compute'), ('bibind.api.container', 'Bibind container')], string='api')
        extra = fields.Text('Extra')
        
        def create_container(self, environnement, container):
            
            return container
        
           
        
        
bibind_container()      
  
  
class bibind_container_image(models.Model):
        _name = "bibind.container.image"
        _description = "image du container"
        
        container_image_id = fields.Char('Id libcloud of the image')
        name = fields.Char('Name')
        path = fields.Char('Path of the image')
        api_driver =fields.Reference(selection=[('cloud.service.api.bibind','api bibind')], string='api')
        version = fields.Char('Version of the image')
        driver = fields.Many2one('bibind.container.driver')
        extra = fields.Text('Extra')
        


bibind_container_image()     
        
        
class bibind_container_cluster(models.Model):
        _name = "bibind.container.cluster"
        _description = "A cluster group for containers"
        
        cluster_id = fields.Char('Id of the cluster')
        name = fields.Char('Name')
       
        driver = fields.Many2one('bibind.container.driver')
        extra = fields.Text('Extra')
        
bibind_container_cluster()       
        
class bibind_container_cluster_location(models.Model):
        _name = "bibind.container.cluster.location"
        _description = "A physical location where clusters can be"
        
        cluster_location_id = fields.Char('Id of the cluster')
        name = fields.Char('Name')
        country = fields.Char('country')
        driver = fields.Many2one('bibind.container.driver')
        
bibind_container_cluster_location()       
        
class bibind_container_driver(models.Model):
        _name = "bibind.container.driver"
        _description = "se ContainerDriver class to derive from"
        
        
        def _get_provider_constante(self):
       
           pro = []
           for key  in DRIVERS: 
               pro.append((key,key))
           return pro
    
    
        name = fields.Char('name du driver')
        provider = fields.Selection(selection='_get_provider_constante')

        @api.onchange('provider')
        def onchange_type(self):
            self.name=self.provider
            
            
bibind_container_driver()



class bibind_rancher_projet(models.Model):
        _name = "bibind.rancher.project"
        _description = "Projet Rancher (old environnement)"
        
        
        
    
    
        name = fields.Char('name rancher project')
        project_name = fields.Char('name du project')
        project_id = fields.Char('name du project')
        
        
        

        @api.onchange('project_name')
        def onchange_type(self):
            self.name=self.project_name
            
            
        def import_projet_rancher(self):
           
            return True
            
            
            
bibind_rancher_projet()