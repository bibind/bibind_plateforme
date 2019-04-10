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

from random import *
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from jinja2 import Environment, FileSystemLoader
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
sys.path.insert(0, "/mnt/extra-addons/bibind/models/bibind_container")
from libcloud.compute.types import Provider
from libcloud.compute.providers import DRIVERS
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment, SSHKeyDeployment
from libcloud.compute.providers import set_driver
from libcloud_bibind.bibindrancher import BibindRancherContainerDriver
import gitlab

set_driver('bibindrancher',
           'libcloud_bibind.bibindrancher',
           'BibindRancherContainerDriver')




_logger = logging.getLogger("bibind_cloudservice")


def generator_password():
    characters = string.ascii_letters + string.punctuation  + string.digits
    password =  "".join(choice(characters) for x in range(randint(8, 16)))
    return password



class bibind_api_container(models.Model ):
    _name = 'bibind.api.container'
    

    name= fields.Char('nom', size=255)
    description= fields.Char('description', size=255)
    driver_cloud = fields.Many2one('bibind.container.driver')
    logge = fields.Text('logue')
     
    def run_driver(self):
        
        driver_run_driver = 'run_driver_'+self.driver_cloud.name
        _logger.info('+ddriver_run_driver %s  ' %(driver_run_driver) )
        fct = getattr(self , driver_run_driver)
        _logger.info('+ddriver_run_driver %s  ' %(fct) )
        bibind_user_id = self.env.user.bibind_user_id        
        medrive = self.env['bibind.me.drivers'].search([('drivers','=',self.driver_cloud.name), ('bibind_user','=', bibind_user_id.id)])
        _logger.info('+ddriver_run_driver %s  ' %(medrive) )      
        if hasattr(self , driver_run_driver):
                fct = getattr(self , driver_run_driver)
                driver =fct(medrive)
                return driver
        else :
            raise Warning(_('Aucune methode implementer pour ce driver .'))
   
    def run_driver_ovh(self, medriver):
        
                Driver = get_driver(Provider.OVH)
                
                driver = Driver(medriver.ovh_applicationkey, medriver.ovh_secretkey, medriver.ovh_projetid, medriver.ovh_consumerkey)
                
                return driver
    
    def run_driver_rancher(self, medriver):
        
                Driver = get_driver('bibindrancher')
               
                driver = Driver(medriver.rancher_accesskey, medriver.rancher_secretkey, medriver.rancher_url, medriver.rancher_port, medriver.rancher_secure)
                
                return driver
    
    
    def run_driver_bibind(self, medriver):
        
                Driver = get_driver('bibindrancher')
                _logger.info('+ddriver_run_driver %s  ' %(medriver.rancher_accesskey) )    
                _logger.info('+ddriver_run_driver %s  ' %(medriver.rancher_secretkey) )    
                _logger.info('+ddriver_run_driver %s  ' %(medriver.rancher_url) )    
                driver = Driver(medriver.rancher_accesskey, medriver.rancher_secretkey, medriver.rancher_secure, medriver.rancher_url, medriver.rancher_port)
                
                return driver
            
            
    def deploy_environnement(self, environnement, type, **kwargs):
        
        solution = environnement.application.category #ex drupal
        type = type #test dev etc
        app = environnement.application.category.name # wordpress, pakage wordpress, drupal, distrib drupal
        depot_app = environnement.application.depot_git
        version = environnement.application.version
        depot = environnement.depot_id.ssh_url
        name = environnement.site_name
        env_id = environnement.rancher_env_id
        password_db = generator_password()
        _logger.info('+doker password compose %s  ' %(name) )  
        _logger.info('+doker password compose %s  ' %(type) )  
        _logger.info('+doker password compose %s  ' %(app) )  
        docker_compose = self._get_docker_compose(name,type, app, password_db)
        rancher_compose = self._get_rancher_compose(name,type, app, password_db)
       
        description = environnement.bibind_user_id.name+'-'+environnement.application.name+'-'+str(environnement.id)
        connection = self.run_driver()
        
        _logger.info('+doker compose %s  ' %(docker_compose) ) 
        _logger.info('+doker compose %s  ' %(rancher_compose) )
        _logger.info('+doker compose %s  ' %(description) ) 
        _logger.info('+doker compose %s  ' %(connection) )       
             
        environment ={}
        external_id = ''
        
        stack = connection.ex_deploy_v2_stack(name, 
                                       description,
                                       env_id, 
                                       docker_compose, 
                                       environment, 
                                       external_id, 
                                       rancher_compose, 
                                     True)
        _logger.info('+doker compose %s  ' %(stack) )  
        return stack
    
    def delete_rancher_stack(self, env_id, stack_id):
        
        connection = self.run_driver()
        stack = connection.ex_destroy_v2_stack(
                                       env_id, 
                                       stack_id) 
        return True
        
    @api.model
    def get_template_paths(self, app):
        _logger.info('+depot path len %s  ' %([os.path.abspath(os.path.join(os.path.dirname(__file__), '..',  'services', 'delivery_continous',app, 'template'))]) )
        return [os.path.abspath(os.path.join(os.path.dirname(__file__), '..',  'services', 'delivery_continous',app,'template'))]

    @api.model
    def create_jinja_env(self,app):
        return Environment(
            loader=FileSystemLoader(
                self.get_template_paths(app)
            )
        )
    
        
    def _get_docker_compose(self,name, type, app, password):
        
        jinja_env = self.create_jinja_env(app)
    
        tmpl = type+'-docker-compose.yml.jinj2'
        template = jinja_env.get_template(tmpl)
        result = template.render(
             
             projetname=name,
             DEV_MYSQL_ROOT_PASSWORD=password
             
        )
        return result
    
    def _get_rancher_compose(self,name, type, app, password):
        
        jinja_env = self.create_jinja_env(app)
    
        tmpl = type+'-rancher-compose.yml.jinj2'
        template = jinja_env.get_template(tmpl)
        result = template.render(
             
             projetname=name,
             
             
        )
        return result
   
    @api.multi
    @api.model
    def get_rancher_environnement(self, delivery):
        
        connection = self.run_driver()
        env = connection.ex_search_env()
        _logger.info('+depot len %s  ' %(delivery) )
        
        for e in env:
            _logger.info('+depot depot %s  ' %(e['name']) )
        
        return env
    
        
    
    
    
    
bibind_api_container()





