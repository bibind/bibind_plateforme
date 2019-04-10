## -*- encoding: utf-8 -*-
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
from libcloud.compute.base import NodeDriver
from libcloud.compute.types import Provider
from libcloud.compute.providers import DRIVERS
from libcloud.compute.providers import get_driver
from libcloud.compute.providers import set_driver

from PIL.EpsImagePlugin import field
#from boto.fps.connection import api_action

_logger = logging.getLogger("bibind_cloudservice")




class cloud_service_node(models.Model):
    _name = 'cloud.service.node'
    
    
    def _get_state_node(self):
        st = [( 'NONODE' , 'Not link'),
              ( 'RUNNING' , 'running'),
              ('STARTING' , 'starting'),
                ('REBOOTING' , 'rebooting'),
                ('TERMINATED' , 'terminated'),
                ('PENDING' , 'pending'),
               ( 'UNKNOWN' , 'unknown'),
                ('STOPPING' , 'stopping'),
                ('STOPPED' , 'stopped'),
                ('SUSPENDED' , 'suspended'),
                ('ERROR' ,'error'),
                ( 'PAUSED' , 'paused'),
                ('RECONFIGURING' , 'reconfiguring'),
                ('MIGRATING' , 'migrating'),
                ('NORMAL' , 'normal')]
        return st
    
    
    idnode = fields.Char('id node')
    UuidMixin = fields.Char('UuidMixin Libcloud ref')
    name = fields.Char('name node')
    region = fields.Char('region node')
    state = fields.Selection(selection='_get_state_node', string='Status')
    public_ips = fields.Char('ip public')
    private_ips =  fields.Char('ip private')
    driver =fields.Many2one('cloud.service.nodedriver', string='Driver')
    api_driver =fields.Reference(selection=[('cloud.service.api.bibind','api bibind')], string='api')
    location = fields.Many2one('cloud.service.nodelocation', string='location')
    size = fields.Many2one('cloud.service.nodesize', string='Size')
    created_date = fields.Datetime('creer le')
    terminated_date = fields.Datetime('terminé le')
    image = fields.Many2one('cloud.service.nodeimage', string='Image')
    extra =fields.Text('extra json type')
   
    
    
    @api.multi
    def valide_size(self):
    
        api = self.api_driver
        driver = api.run_bibind_driver()
        size_id = self.size.id_size
        self.extra = driver.ex_get_size_json_extra(size_id)
        
    @api.multi
    def start_node(self):
        
        api = self.api_driver
        
        
        img = self.image
        nodesize= self.size 
        nodelocation = self.location
        _logger.info('+vimage extr %s  ' %(img.id_image) )
        _logger.info('+vimage extr %s  ' %(nodesize.id) )
        _logger.info('+vimage extr %s  ' %(nodelocation.id_location) )
        driver = api.run_driver()
        location = [l for l in driver.list_locations() if l.id == nodelocation.id_location][0]
        image = [i for i in driver.list_images() if img.id_image == i.id][0]
        size = [s for s in driver.list_sizes() if s.id == nodesize.id_size][0]
        
        startnode = driver.create_node(name=self.name, size=size, image=image,
                                  location=location)
        _logger.info('+vimage extr %s  ' %(startnode) )
        _logger.info('+vimage extr %s  ' %(startnode.extra) )
        
        val = api.converti_nodelibcloud_to_nodebibind(startnode, size)
        
        self.update(val)
        
        
        
    
       
    def reboot_node(self):
        
        api = self.api_driver
        api.reboot_node(self.idnode)
    
    @api.multi
    def confirme_destroy_node(self):
        
        return {
                'name': 'Node destroy Confirmation',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'wizard.destroy.confirm',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'context':{'node_id':self.id},
                'target': 'new',
                
                }
    
    @api.multi   
    def destroy_node(self):
        
        Driver_api = self.api_driver.run_driver()
        node = self.ex_get_node()
        delete = Driver_api.destroy_node(node)
        if delete:
            self.state = 'TERMINATED'
            self.terminated_date = fields.datetime.now()
            return delete
    
    @api.multi
    def terminated_node(self):
        self.state = 'TERMINATED'
        self.terminated_date = fields.datetime.now()
          
        
    def ex_get_node(self):
        
        Driver_api = self.api_driver.run_driver()
        try :
            node = Driver_api.ex_get_node(self.idnode)
            return node
        except TypeError:
            
            return False
        
    def get_list_keys_pair(self):
        
        Driver_api = self.api_driver.run_driver()
        try :
            list = Driver_api.list_key_pairs()
            return list
        except TypeError:
            
            return False
    
    def after_pending_state(self):
        api = self.api_driver
        node = self.ex_get_node()
        state = node.state.upper()
        
        if(state in ('STARTING','PENDING')):
            return False
        if(state == 'RUNNING'):
            return True
            
          
    @api.multi    
    def ex_get_state_node(self):
        api = self.api_driver
        node = self.ex_get_node()
        state = node.state.upper()
        self.extra = state;
        
    
    
    def run_node(self):
        
        api = self.api_driver
        node = self.create_node()
        state = node.state.upper()
        self.signal_workflow('node_run')
        
        return True
    
    def is_pending(self):
        
        self.signal_workflow('node_run')
        
        return True
    
    def is_running(self):
        
        self.signal_workflow('node_run')
        
        return True
    
    @api.multi
    def get_log_node(self):
        
        node = self.ex_get_node()
        if node:
            list = self.get_list_keys_pair()
            if node.extra:
                self.extra = list
               
            else:
                self.extra = list
                
        else:
            self.state = 'TERMINATED'
            self.extra = self._name+','+str(self.id)
            if not self.terminated_date:
                self.terminated_date = fields.datetime.now()   
       

cloud_service_node()        
        
        
        
        
        
class cloud_service_nodedriver(models.Model):
   
    _name = 'cloud.service.nodedriver'
    
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
    
cloud_service_nodedriver()

class cloud_service_nodesize(models.Model):
   
    _name = 'cloud.service.nodesize'
    
    ref_api = fields.Many2one('cloud.service.api.fournisseur')
    id_size = fields.Char('id size')
    UuidMixin = fields.Char('UuidMixin Libcloud ref')
    name = fields.Char('name size')
    region = fields.Char('region size')
    ram = fields.Integer( string='Amount of memory (in MB)')
    disk = fields.Integer(' Amount of disk storage (in GB)')
    bandwidth =  fields.Integer(' Amount of bandiwdth included with this size')
    driver = fields.Many2one('cloud.service.nodedriver', string='Driver')
    bibindapi_id = fields.Many2one('cloud.service.api.bibind', string='Api')
    price = fields.Float(string='Price (in US dollars) of running this node for an hour')
    extra =fields.Text('Optional provider specific attributes associated with this size')
    log = fields.Text('log')
    
    
    
    
    
    
    @api.multi
    def get_extra(self):
        
        bibindapi = self.bibindapi_id
        
        nodesize = bibindapi.get_size_extra(self.id_size)
        self.log = nodesize
        
   
    
cloud_service_nodesize()    



class cloud_service_nodeimage(models.Model):
   
    _name = 'cloud.service.nodeimage'

    
    id_image = fields.Char('id image')
    UuidMixin = fields.Char('UuidMixin Libcloud ref')
    name = fields.Char('name image')
    driver = fields.Many2one('cloud.service.nodedriver', string=' Driver this image belongs to')
    extra =fields.Text('Optional provided specific attributes associated withthis image')
    

cloud_service_nodeimage()


class cloud_service_nodelocation(models.Model):
   
    _name = 'cloud.service.nodelocation'

            
    id_location = fields.Char('Location ID')
    name = fields.Char('Location name ')
    country = fields.Char('Location country ')
    driver =fields.Many2one('cloud.service.nodedriver', string=' Driver this location belongs to.')
    
    

cloud_service_nodelocation()



class cloud_service_nodeAuthSSHKey(models.Model):
   
    _name = 'cloud.service.nodeauthsshkey'

            
    
    pubkey = fields.Char('Public key matetiral')
 
    

cloud_service_nodeAuthSSHKey()


class cloud_service_nodeAuthPassword(models.Model):
   
    _name = 'cloud.service.nodeauthpassword'

            
    password = fields.Char('Public key matetiral')
    generated = fields.Boolean('Public key matetiral')
    
 
    

cloud_service_nodeAuthPassword()



class cloud_service_StorageVolume(models.Model):
   
    _name = 'cloud.service.storagevolume'

    def _get_volume_state(self):
        state = [
            ('AVAILABLE' , 'available'),
            ('ERROR' , 'error'),
            ('INUSE' , 'inuse'),
            ('CREATING' , 'creating'),
            ('DELETING' , 'deleting'),
            ('DELETED' , 'deleted'),
            ('BACKUP' , 'backup'),
            ('ATTACHING' , 'attaching'),
            ('UNKNOWN' , 'unknown'),
            ('MIGRATING' , 'migrating')   
            ]
        return state

    
    id_storage = fields.Char('id: Storage volume ID.')
    UuidMixin = fields.Char('UuidMixin Libcloud volume ref')
    name = fields.Char('Storage volume name')
    size = fields.Integer(string='Size of this volume (in GB)')
    state = fields.Selection(selection ='_get_volume_state', string='Optional state of the StorageVolume. If not provided, will default to UNKNOWN')
    driver =fields.Many2one('cloud.service.nodedriver', string=' Driver this location belongs to.')
    extra =fields.Text('Optional provider specific attributes.')
    
    
    def list_snapshot(self):
        
        driver = self.driver
        return driver.list_volume_snapshots(self)
    
    def attach(self, node, device=None):
        """
        Attach this volume to a node.

        :param node: Node to attach volume to
        :type node: :class:`.Node`

        :param device: Where the device is exposed,
                            e.g. '/dev/sdb (optional)
        :type device: ``str``

        :return: ``True`` if attach was successful, ``False`` otherwise.
        :rtype: ``bool``
        """

        return self.driver.attach_volume(node=node, volume=self, device=device)

    def detach(self):
        """
        Detach this volume from its node

        :return: ``True`` if detach was successful, ``False`` otherwise.
        :rtype: ``bool``
        """

        return self.driver.detach_volume(volume=self)

    def snapshot(self, name):
        """
        Creates a snapshot of this volume.

        :return: Created snapshot.
        :rtype: ``VolumeSnapshot``
        """
        return self.driver.create_volume_snapshot(volume=self, name=name)

    def destroy(self):
        """
        Destroy this storage volume.

        :return: ``True`` if destroy was successful, ``False`` otherwise.
        :rtype: ``bool``
        """

        return self.driver.destroy_volume(volume=self)

    
cloud_service_StorageVolume()


class cloud_service_VolumeSnapshot(models.Model):
   
    _name = 'cloud.service.volumesnapshot'
    
    
    def _get_snapshot_state(self):
        
        state =[
            ('AVAILABLE' , 'available'),
            ('ERROR' , 'error'),
            ('INUSE' , 'inuse'),
            ('CREATING' , 'creating'),
            ('DELETING' , 'deleting'),
            ('DELETED' , 'deleted'),
            ('BACKUP' , 'backup'),
            ('ATTACHING' , 'attaching'),
            ('UNKNOWN' , 'unknown'),
            ('MIGRATING' , 'migrating')
            ]
        return state
    
    
    """
        VolumeSnapshot constructor.
        
    :param      id: Snapshot ID.
    :type       id: ``str``

    :param      driver: The driver that represents a connection to the
                            provider
    :type       driver: `NodeDriver`

    :param      size: A snapshot size in GB.
    :type       size: ``int``

    :param      extra: Provider depends parameters for snapshot.
    :type       extra: ``dict``

    :param      created: A datetime object that represents when the
                             snapshot was created
    :type       created: ``datetime.datetime``

    :param      state: A string representing the state the snapshot is
                           in. See `libcloud.compute.types.StorageVolumeState`.
    :type       state: ``str``

    :param      name: A string representing the name of the snapshot
    :type       name: ``str``
        """
    id_snapshot = fields.Char('snapshot ID.')
    driver = fields.Many2one('cloud.service.nodedriver', string=' The driver that represents a connection to the provider')
    size = fields.Integer(string='snapshot size in GB.')
    extra = fields.Text(string='Provider depends parameters for snapshot.')
    created = fields.Datetime(string='A datetime object that represents when the snapshot was created')
    state = fields.Selection(selection='_get_snapshot_state', string=' string representing the state the snapshot is in. See `libcloud.compute.types.StorageVolumeState')
    name = fields.Char(string='A string representing the name of the snapshot')
            
    
    

cloud_service_VolumeSnapshot()