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
sys.path.insert(0, "/mnt/extra-addons/bibind/models/bibind_api")
from libcloud.compute.types import Provider
from libcloud.compute.providers import DRIVERS
from libcloud.compute.providers import get_driver
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment, SSHKeyDeployment
from libcloud.compute.providers import set_driver
from libcloud_bibind.bibind import BibindNodeDriver
import gitlab

set_driver('bibind',
           'libcloud_bibind.bibind',
           'BibindNodeDriver')




_logger = logging.getLogger("bibind_cloudservice")


def generator_password():
    characters = string.ascii_letters + string.punctuation  + string.digits
    password =  "".join(choice(characters) for x in range(randint(8, 16)))
    return password


class cloud_service_api_fournisseur(models.Model):
    _name = 'cloud.service.api.fournisseur'
   
   
   
    
    name = fields.Char('nom', size=255)
    res_partner_id = fields.Many2one(comodel_name='res.partner', string='Fournisseur')
   
    description =fields.Text('description')  
    ref_api = fields.Reference(selection=[('cloud.service.api.bibind','api bibind')] )
    
    
    
    
    def create_host(self, service_fournisseur):
        
        
        host = self.ref_api.create_host(service_fournisseur)
        
        return host
        
        
        
        
    

    def get_model_api_ref(self):
        
        self.description = 'hello endpoint: %s et url id %s' %(self.api_ref.endpoint, self.api_ref.requeteapiids.url)
        
        

    def destroy_host(self, host):
        
        self.description = 'hello endpoint: %s et url id %s' %(self.api_ref.endpoint, self.api_ref.requeteapiids.url)
       
        
cloud_service_api_fournisseur()






        
        
        
class Cloud_Service_api_bibind(models.Model, BibindNodeDriver ):
    _name = 'cloud.service.api.bibind'
    
    _inherit = 'cloud.service.nodedriver'
    
    def _get_location(self):
        location = [
            ('SBG1','Strasbourg 1'),
            ('BHS1', 'Montreal 1'),
            ('GRA1', 'Gravelines 1'),
            ]
        return location

    def _get_entpoint(self):
        
        
           pro = []
           for key  in ovh.client.ENDPOINTS  : 
               pro.append((key,key))
           return pro 
       

    def verif_image_import(self):
            
        if self.driver_cloud : 
            _logger.info('+verfiy list %s  ' %(self.driver_cloud.name) )   
            listr =self.env['cloud.service.nodeimage'].search([('driver.name','=', self.driver_cloud.name)])
            _logger.info('+verfiy list %s  ' %(self.driver_cloud.name) )
            _logger.info('+verfiy list %s  ' %(len(listr)>0) )
            if len(listr)>0:
                 self.importimages = 1
            else:
                 self.importimages = 0
        else :
            self.importimages = 0
    
    
    
    
    
    

    def verif_size_import(self):
             
        if self.driver_cloud :
             listr =self.env['cloud.service.nodesize'].search([('driver.name','=', self.driver_cloud.name)])
             
             if len(listr)>0:
                self.importsize = 1
             else:
                self.importsize = 0
        else :
            self.importsize = 0

    def verif_location_import(self):
             
        if self.driver_cloud :
             listr =self.env['cloud.service.nodelocation'].search([('driver.name','=', self.driver_cloud.name)])
             
             if len(listr)>0:
                self.importlocation = 1
             else:
                self.importlocation = 0
        else :
            self.importlocation = 0
            

    def verif_node_import(self):
             
        if self.driver_cloud :
             listr =self.env['cloud.service.node'].search([('driver.name','=', self.driver_cloud.name)])
             
             if len(listr)>0:
                self.importnode = 1
             else:
                self.importnode = 0
        else :
            self.importnode = 0
        
    name= fields.Char('nom', size=255)
    description= fields.Char('description', size=255)
    auth_param = fields.Many2one('bibind.me.drivers')
    location = fields.Selection(selection='_get_location', string='Location')
    endpoint = fields.Selection(selection='_get_entpoint',string='endpoint',help='choisir lendpoint' )
    applicationkey =fields.Char('applicationkey', required=True)
    secretkey = fields.Char('secret key', required=True)
    consumerkey = fields.Char('Consumer key', required=True)
    projetid = fields.Char('projet Id', required=True)
    driver_cloud = fields.Many2one('cloud.service.nodedriver')
    importimages = fields.Integer(compute='verif_image_import', string='images importées')
    importsize = fields.Integer( compute='verif_size_import', string='sizes importées')
    importlocation = fields.Integer(compute='verif_location_import', string='locations importées')
    importnode = fields.Integer( compute='verif_node_import', string='nodes importées')
   
    logge = fields.Text('logue')
    
    @api.onchange('importimages')
    def onchange_importimages(self):
        
        if self.driver_cloud : 
            _logger.info('+verfiy list %s  ' %(self.driver_cloud.name) )   
            listr =self.env['cloud.service.nodeimage'].search([('driver.name','=', self.driver_cloud.name)])
            _logger.info('+verfiy list %s  ' %(self.driver_cloud.name) )
            _logger.info('+verfiy list %s  ' %(len(listr)>0) )
            if len(listr)>0:
                 self.importimages = 1
            else:
                 self.importimages = 0
        else :
            self.importimages = 0
    
    
    def get_size_extra(self, nodeid):
        client = ovh.Client(endpoint='ovh-eu')
        zone = '/cloud/project/%s/flavor/%s'%(self.projetid, nodeid)
        params ={}
        params['flavorId'] = nodeid
        nodeextra = client.get(zone) 
        
        return nodeextra
    
    
    @api.onchange('importsize')
    def onchange_size_import(self):
             
        if self.driver_cloud :
             listr =self.env['cloud.service.nodesize'].search([('driver.name','=', self.driver_cloud.name)])
             
             if len(listr)>0:
                 self.importsize = 1
             else:
                 self.importsize = 0
        else :
            self.importsize = 0
    
    
    
    def run_driver(self):
            Driver = get_driver(Provider.OVH)
            
            driver = Driver(self.applicationkey, self.secretkey, self.projetid, self.consumerkey)
            
            return driver
        
    def run_rancher_driver(self):
            Driver = get_driver(Provider.RANCHER)
            
            driver = Driver(self.applicationkey, self.secretkey, self.projetid, self.consumerkey)
            
            return driver
        
    def run_bibind_driver(self):
            Driver = get_driver('bibind')
            
            driver = Driver(self.applicationkey, self.secretkey, self.projetid, self.consumerkey)
            
            return driver
    
    def run_user_driver(self, user_auth):
            
            Driver = get_driver(user_auth.driver)
            
            driver = Driver(user_auth.applicationkey,user_auth.secretkey, user_auth.projetid, user_auth.consumerkey)
            
            return driver
    
    

    def import_list_size(self):
        
        if self.importsize==0:
            driver = self.run_driver()
            list_sizes = driver.list_sizes()
            nodesize = self.env['cloud.service.nodesize']
            for size in list_sizes:
                if not size.extra['region']:
                    region = 'inconnu'
                else:
                    region = size.extra['region']
                
                val = {
                     'id_size' : size.id,
                     'UuidMixin' : size.uuid,
                     'name' : size.name,
                     'region':region,
                     'driver' : self.driver_cloud.id
                          }
                if size.ram !=None:
                    val.update(
                        { 'ram' : size.ram }
                        )
                if size.disk !=None:
                    val.update(
                        { 'disk' : size.disk }
                        )
                if size.bandwidth !=None:
                    val.update(
                        { 'bandwidth' :  size.bandwidth}
                        )
                if size.price !=None:
                    val.update(
                        { 'price' : size.price}
                        )
                if size.extra !=None:
                    val.update(
                        { 'extra' : size.extra}
                        )
                
                nodesize.create(val)
        else :
            raise Warning('La liste des images pour ce driver a déjà été importé')
    
            
            
    def verify_list_size(self):
        
        list =self.env['cloud.service.nodesize'].name_search(['driver.name','=', self.driver_cloud.name])
        odoo_size = len(list)
        driver = self.run_driver()
        list_sizes = driver.list_sizes()
        libcloudsize = len(list_sizes)
        if odoo_size==libcloudsize:
            return True
        else:
            return False

    def verify_list_image(self):
        
        list =self.env['cloud.service.nodeimage'].name_search(['driver.name','=', self.driver_cloud.name])
        _logger.info('+verfiy list %s  ' %(list) )
        odoo_images = len(list)
        driver = self.run_driver()
        list_images = driver.list_images()
        libcloudimages = len(list_images)
        if odoo_images==libcloudimages:
            
            return True
        else:
            return False
    
    

    def import_list_images(self):
        
        if not self.importimages:
            driver = self.run_driver()
            list_images = driver.list_images()
            
            nodesize = self.env['cloud.service.nodeimage']
            for image in list_images:
                
            
                val = {
                     'id_image' : image.id,
                     'UuidMixin' : image.uuid,
                     'name' : image.name,
                     'driver' : self.driver_cloud.id
                          }
                
                
                if image.extra !=None:
                    val.update(
                        { 'extra' : image.extra}
                        )
                
                nodesize.create(val)
                self.importimages =True
        else:
            raise Warning('La liste des serveurs ont déjà été importer')
    

    def import_list_location(self):
        
        if self.importlocation==0:
            driver = self.run_bibind_driver()
            list_sizes = driver.list_locations()
            nodeslocation = self.env['cloud.service.nodelocation']
            for location in list_sizes:
                
                val = {
                     'id_location' : location.id,
                     'country' : location.country,
                     'name' : location.name,
                     'driver' : self.driver_cloud.id
                          }
                
                
                nodeslocation.create(val)
        else :
            raise Warning('La liste des images pour ce driver a déjà été importé')
    
    def get_size_by_attr(self, size_extra):
        
        return self.env['cloud.service.nodesize'].search([('id_size','=',size_extra)])[0].id
    
    def get_image_by_attr(self, image_extra):
        _logger.info('+vimage extr %s  ' %(image_extra) )
        image =  self.env['cloud.service.nodeimage'].search([('id_image','=',image_extra)])
        _logger.info('+vimage extr %s  ' %(image) )
        
        return image.id
        
    def converti_nodelibcloud_to_nodebibind(self, node, size=None):
            if not node.extra['region']:
                region = 'inconnu'
            else:
                region = node.extra['region']
                
            if 'flavorId' in node.extra:
                size_id = node.extra['flavorId']
            else:
                size_id = node.extra['flavor']['id']
                
            if 'imageId' in node.extra:
                image_id = node.extra['imageId']
            else:
                image_id = node.extra['image']['id']
            if 'created' in node.extra:
                tt = "%Y-%m-%dT%H:%M:%SZ"
                created = datetime.strptime(node.extra['created'], tt)
            else:
                created = datetime.date.today()
            
            
            val = {
                     'idnode' : node.id,
                     'UuidMixin' : node.uuid,
                     'name' : node.name,
                     'region' : region,
                     'driver' : self.driver_cloud.id,
                     'api_driver': self._name+','+str(self.id),
                     'state' : node.state.upper(),
                     'public_ips' : node.public_ips,
                     'private_ips' : node.private_ips,
                     'size' : self.get_size_by_attr(size_id),
                     'created_date' : created,
                     'image' : self.get_image_by_attr(image_id),
                     'extra' : node.extra ,
                          
                          }
            return val
    

    def import_list_node(self):
        
        
        if self.importnode==0:
            driver = self.run_driver()
            list_nodes = driver.list_nodes()
            if(len(list_nodes)>0):
                nodes = self.env['cloud.service.node']
                for node in list_nodes:
                    
                    val = self.converti_nodelibcloud_to_nodebibind(node)           
                    
                    nodes.create(val)
            else :
                return True
        else :
            raise Warning('La liste des images pour ce driver a déjà été importé')
         
    
    
    
    
        
    
    def create_host(self, service_fournisseur):
        
        img = service_fournisseur.image
        size_fournisseur= service_fournisseur.sizefournisseur 
        location = service_fournisseur.locationfournisseur
        _logger.info('+vimage extr %s  ' %(img.id_image) )
        _logger.info('+vimage extr %s  ' %(size_fournisseur.id) )
        _logger.info('+vimage extr %s  ' %(location.id_location) )
        driver = self.run_driver()
        location = [l for l in driver.list_locations() if l.id == location.id_location][0]
        image = [i for i in driver.list_images() if img.id_image == i.id][0]
        size = [s for s in driver.list_sizes() if s.id == size_fournisseur.id_size][0]
        
        node = driver.create_node(name='myserveur', size=size, image=image,
                                  location=location)
        _logger.info('+vimage extr %s  ' %(node) )
        _logger.info('+vimage extr %s  ' %(node.extra) )
        nodemodel = self.env['cloud.service.node']
        val = self.converti_nodelibcloud_to_nodebibind(node, size)
        
        host =  nodemodel.create(val)
        return host
    

    def deploy_host(self, fournisseur,  host):
    
        name = host.name
        bibind_image = host.image
        bibind_size = host.size
        bibind_location = host.location
        
        _logger.info('+ idimage %s  ' %(bibind_image.id_image) )
        _logger.info('+ size %s  ' %(bibind_size) )
        _logger.info('+v location extr %s  ' %(bibind_location) )
        
        driver = self.run_bibind_driver()
    
        img = driver.get_image(bibind_image.id_image)
        _logger.info('+ idimage gggg%s  ' %(img) )
        location = [l for l in driver.list_locations() if l.id == bibind_location.id_location][0]
        image = [i for i in driver.list_images() if bibind_image.id_image == i.id][0]
        size = [s for s in driver.list_sizes() if s.id == bibind_size.id_size][0]
        
      
        step = []
        # Shell script to run on the remote server
        for script in host.deploy_scripts_ids:
            _logger.info('+vscript host  %s  ' %(script) )
            myscript = self.env['launch.script'].browse(script.id)
            _logger.info('+vscript host  %s  ' %(myscript.script_code) )
            step.append(ScriptDeployment(str(myscript.script_code)))
            _logger.info('+vscript host  %s  ' %(step) )
            
            
        
       

        msd = MultiStepDeployment(step)
        _logger.info('+vimage  %s  ' %(driver) )
        
        params ={}
        params['deploy'] =msd
        params['ssh_username'] ='debian'
        params['ssh_key']='/var/lib/odoo/.ssh/id_rsa'
        # deploy_node takes the same base keyword arguments as create_node.
        node = driver.deploy_node(name=name, image=image, size=size,location=location,ex_keyname='bibind',**params )
        _logger.info('+node  %s  ' %(node) )
        nodemodel = self.env['cloud.service.node']
        val = self.converti_nodelibcloud_to_nodebibind(node, size)

        bibindnode =  nodemodel.create(val)
        return bibindnode
    
    
    def deploy_script(self, fournisseur,  host):
        
        
        _logger.info('+vscript host  %s  ' %(host) )
        _logger.info('+vscript host  %s  ' %(host.id) )
        hostid = self.env['bibind.host'].browse(host.id)
        _logger.info('+vscript host  %s  ' %(host) )
        bibindnode = host.nodeid
        _logger.info('+vscript host  %s  ' %(host) )
        _logger.info('+vscript host  %s  ' %(bibindnode.idnode) )
        driver = self.run_driver()
        _logger.info('+vscript host  %s  ' %(driver) )
        
       
        
        node = driver.ex_get_node(str(bibindnode.idnode))
        
        ip_address = node.public_ips
        _logger.info('+vscript host  %s  ' %(node) )
        _logger.info('+vscript ip_address  %s  ' %(ip_address) )
        _logger.info('+vscript ip_address[0]  %s  ' %(ip_address[0]) )
        
        step=[]
        # Shell script to run on the remote server
        for script in host.deploy_scripts_ids:
            _logger.info('+vscript host  %s  ' %(script) )
            myscript = self.env['launch.script'].browse(script.id)
            _logger.info('+vscript host  %s  ' %(myscript.script_code) )
            step.append( ScriptDeployment(str(myscript.script_code)))
            _logger.info('+vscript host  %s  ' %(step) )


        msd = MultiStepDeployment(step)
        _logger.info('+vimage  %s  ' %(driver) )
        SSH_CONNECT_TIMEOUT = 1 * 60
        ssh_timeout = 10 
        timeout = SSH_CONNECT_TIMEOUT
        max_tries = 3
        params ={}
        params['deploy'] =msd
        params['ssh_username'] ='debian'
        params['ssh_key']='/var/lib/odoo/.ssh/id_rsa'
        # deploy_node takes the same base keyword arguments as create_node.
        node = driver._connect_and_run_deployment_script(
                    task=msd, node=node,
                    ssh_hostname=ip_address[0], ssh_port=22,
                    ssh_username='debian', ssh_password='',
                    ssh_key_file='/var/lib/odoo/.ssh/id_rsa', ssh_timeout=ssh_timeout,
                    timeout=timeout, max_tries=max_tries)
        return bibindnode
    
    
    def deploy_specific_script(self, host, script):
        
        
        
        hostid = self.env['bibind.host'].browse(host.id)
       
        bibindnode = host.nodeid
        driver = self.run_driver()
        _logger.info('+vscript host  %s  ' %(driver) )
        
       
        
        node = driver.ex_get_node(str(bibindnode.idnode))
        
        ip_address = node.public_ips
        _logger.info('+vscript node  %s  ' %(node) )
        _logger.info('+vscript ip_address  %s  ' %(ip_address) )
        _logger.info('+vscript ip_address[0]  %s  ' %(ip_address[0]) )
        
        step=[]
        step.append( ScriptDeployment(str(script.script_code)))
   
       
        msd = MultiStepDeployment(step)
        _logger.info('+driver  %s  ' %(step) )
        
        _logger.info('+vscript ip_address[0]  %s  ' %(msd) )
        
       
        SSH_CONNECT_TIMEOUT = 1 * 60
        ssh_timeout = 10 
        timeout = SSH_CONNECT_TIMEOUT
        max_tries = 3
        params ={}
        params['deploy'] =msd
        params['ssh_username'] ='debian'
        params['ssh_key']='/var/lib/odoo/.ssh/id_rsa'
        # deploy_node takes the same base keyword arguments as create_node.
        node = driver._connect_and_run_deployment_script(
                    task=msd, node=node,
                    ssh_hostname=ip_address[0], ssh_port=22,
                    ssh_username='debian', ssh_password='',
                    ssh_key_file='/var/lib/odoo/.ssh/id_rsa', ssh_timeout=ssh_timeout,
                    timeout=timeout, max_tries=max_tries)
        return node
    
    
    def deploy_config_depot_script(self, host, service, env, param):
        
        
        SCRIPT = '''#!/usr/bin/env bash
                cd /home && sudo mkdir apt-get -y update && apt-get -y install puppet
                '''
        
        hostid = self.env['bibind.host'].browse(host.id)
       
        bibindnode = host.nodeid
        driver = self.run_driver()
        _logger.info('+vscript host  %s  ' %(driver) )
        
       
        
        node = driver.ex_get_node(str(bibindnode.idnode))
        
        ip_address = node.public_ips
        _logger.info('+vscript node  %s  ' %(node) )
        _logger.info('+vscript ip_address  %s  ' %(ip_address) )
        _logger.info('+vscript ip_address[0]  %s  ' %(ip_address[0]) )
        
        step=[]
        step.append( ScriptDeployment(str(script.script_code)))
   
       
        msd = MultiStepDeployment(step)
        _logger.info('+driver  %s  ' %(step) )
        
        _logger.info('+vscript ip_address[0]  %s  ' %(msd) )
        
       
        SSH_CONNECT_TIMEOUT = 1 * 60
        ssh_timeout = 10 
        timeout = SSH_CONNECT_TIMEOUT
        max_tries = 3
        params ={}
        params['deploy'] =msd
        params['ssh_username'] ='debian'
        params['ssh_key']='/var/lib/odoo/.ssh/id_rsa'
        # deploy_node takes the same base keyword arguments as create_node.
        node = driver._connect_and_run_deployment_script(
                    task=msd, node=node,
                    ssh_hostname=ip_address[0], ssh_port=22,
                    ssh_username='debian', ssh_password='',
                    ssh_key_file='/var/lib/odoo/.ssh/id_rsa', ssh_timeout=ssh_timeout,
                    timeout=timeout, max_tries=max_tries)
        return node
    
    
    def _get_script_lb_rancher_service(self, name):
        
        
        return lb
    
    def _get_script_wordpres_rancher_compose(self,client):
        
        
        return ranchercompose
    
    
    def _get_script_wordpres_docker_compose(self, client):
        
            dockercompose ="""'
                version: "2"
            services:
              {projetname}-live:
                image: wordpress
                stdin_open: true
                tty: true
                links:
                - {projetname}-db-live:mysql
                ports:
                - 8086:80/tcp
                labels:
                  io.rancher.container.pull_image: always
              {projetname}-db-dev:
                image: mariadb
                environment:
                  MYSQL_ROOT_PASSWORD: my-secret-pw
                stdin_open: true
                tty: true
                labels:
                  io.rancher.container.pull_image: always
              {projetname}-test:
                image: wordpress
                stdin_open: true
                tty: true
                links:
                - {projetname}-db-test:mysql
                ports:
                - 8085:80/tcp
                labels:
                  io.rancher.container.pull_image: always
              {projetname}-db-test:
                image: mariadb
                environment:
                  MYSQL_ROOT_PASSWORD: wordpresstest
                stdin_open: true
                tty: true
                labels:
                  io.rancher.container.pull_image: always
              {projetname}-db-live:
                image: mariadb
                environment:
                  MYSQL_ROOT_PASSWORD: wordpresslive
                stdin_open: true
                tty: true
                labels:
                  io.rancher.container.pull_image: always
              {projetname}-dev:
                image: wordpress
                stdin_open: true
                tty: true
                links:
                - {projetname}-db-dev:mysql
                ports:
                - 8084:80/tcp
                labels:
                  io.rancher.container.pull_image: always
            
            '"""
            
            return dockercompose
    
    def import_template_app(self):
        
        return True
    
    
    def deploy_service(self, fournisseur, host, service):
        
        scripts = service.template_id.script
        
       
        hostid = self.env['bibind.host'].browse(host.id)
        
        bibindnode = host.nodeid
       
      
        driver = self.run_driver()
        _logger.info('+vscript host  %s  ' %(driver) )
        
        name = service.type+'-'+service.partner_id.name+'-'+service.id   
            
        stack =   driver.ex_deploy_stack( name, 
                        description=None, docker_compose=None,
                        environment=None, external_id=None,
                        rancher_compose=None, start=True)
        
        node = driver.ex_get_node(str(bibindnode.idnode))
        
        ip_address = node.public_ips
        _logger.info('+vscript host  %s  ' %(node) )
        _logger.info('+vscript ip_address  %s  ' %(ip_address) )
        _logger.info('+vscript ip_address[0]  %s  ' %(ip_address[0]) )
        
        step=[]
        # Shell script to run on the remote server
        for script in host.deploy_scripts_ids:
            _logger.info('+vscript host  %s  ' %(script) )
            myscript = self.env['launch.script'].browse(script.id)
            _logger.info('+vscript host  %s  ' %(myscript.script_code) )
            step.append( ScriptDeployment(str(myscript.script_code)))
            _logger.info('+vscript host  %s  ' %(step) )


        msd = MultiStepDeployment(step)
        _logger.info('+vimage  %s  ' %(driver) )
        SSH_CONNECT_TIMEOUT = 1 * 60
        ssh_timeout = 10 
        timeout = SSH_CONNECT_TIMEOUT
        max_tries = 3
        params ={}
        params['deploy'] =msd
        params['ssh_username'] ='debian'
        params['ssh_key']='/var/lib/odoo/.ssh/id_rsa'
        # deploy_node takes the same base keyword arguments as create_node.
        node = driver._connect_and_run_deployment_script(
                    task=msd, node=node,
                    ssh_hostname=ip_address[0], ssh_port=22,
                    ssh_username='debian', ssh_password='',
                    ssh_key_file='/var/lib/odoo/.ssh/id_rsa', ssh_timeout=ssh_timeout,
                    timeout=timeout, max_tries=max_tries)
        return bibindnode
        
   
    def getlistUrl(self):
        
        return
    
    
Cloud_Service_api_bibind()








