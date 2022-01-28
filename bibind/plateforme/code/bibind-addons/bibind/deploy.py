#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import with_statement
"""
Provides base classes for working with drivers
"""
import logging
 
from logging.handlers import RotatingFileHandler

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')

 

steam_handler = logging.StreamHandler()
steam_handler.setLevel(logging.DEBUG)
logger.addHandler(steam_handler)



import sys
import time
import hashlib
import os
import tempfile
import socket
import random
import binascii
import subprocess

from libcloud.utils.py3 import b

import libcloud.compute.ssh
from libcloud.pricing import get_size_price
from libcloud.compute.types import NodeState, StorageVolumeState,\
    DeploymentError
from libcloud.compute.ssh import SSHClient
from libcloud.common.base import ConnectionKey
from libcloud.common.base import BaseDriver
from libcloud.common.types import LibcloudError
from libcloud.compute.ssh import have_paramiko

from libcloud.utils.networking import is_private_subnet
from libcloud.utils.networking import is_valid_ip_address

if have_paramiko:
    from paramiko.ssh_exception import SSHException
    from paramiko.ssh_exception import AuthenticationException

    SSH_TIMEOUT_EXCEPTION_CLASSES = (AuthenticationException, SSHException,
                                     IOError, socket.gaierror, socket.error)
else:
    SSH_TIMEOUT_EXCEPTION_CLASSES = (IOError, socket.gaierror, socket.error)

# How long to wait for the node to come online after creating it
NODE_ONLINE_WAIT_TIMEOUT = 10 * 60

# How long to try connecting to a remote SSH server when running a deployment
# script.
SSH_CONNECT_TIMEOUT = 5 * 60

from pprint import pprint
from libcloud.compute.deployment import MultiStepDeployment
from libcloud.compute.deployment import ScriptDeployment, SSHKeyDeployment
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.providers import set_driver

from libcloud.common.ovh import API_ROOT, OvhConnection
from libcloud.compute.base import (NodeDriver, NodeSize, Node, NodeLocation,
                                   NodeImage, StorageVolume, VolumeSnapshot)
from libcloud.compute.types import (Provider, StorageVolumeState,
                                    VolumeSnapshotState)
from libcloud.compute.drivers.openstack import OpenStackNodeDriver
from libcloud.compute.drivers.openstack import OpenStackKeyPair
from libcloud.compute.drivers.ovh import OvhNodeDriver

import gitlab
from jinja2 import Environment, PackageLoader

set_driver('bibind',
           'tests.bibind',
           'BibindNodeDriver')

# rancher
# cle acces
# 5B8D466780146E519CA7 
# Cle secrete (mot de passe)
# frWiggMWWCb2CeZVvLr5uqzS6KgAYLRWS96kF8sB 
# list =driver.list_nodes()
# 
# pprint(list)
# 
# id = driver.ex_get_node('585e104f-5524-452b-a94f-61292dfe9584')
# print(id.uuid)

BIBINDLOCATIONS = {
    "BHS": {"id": "BHS", "name": "Beauharnois, Quebec ", "country": "CA"},
    "BHS1": {"id": "BHS1", "name": "Beauharnois, Quebec 1", "country": "CA"},
    "BHS2": {"id": "BHS2", "name": "Beauharnois, Quebec 2", "country": "CA"},
    "BHS3": {"id": "BHS3", "name": "Beauharnois, Quebec 3", "country": "CA"},
    "BHS4": {"id": "BHS4", "name": "Beauharnois, Quebec 4", "country": "CA"},
    "BHS5": {"id": "BHS5", "name": "Beauharnois, Quebec 5", "country": "CA"},
    "BHS6": {"id": "BHS6", "name": "Beauharnois, Quebec 6", "country": "CA"},
    "DC1": {"id": "DC1", "name": "Paris DC1", "country": "FR"},
    "FRA1": {"id": "FRA1", "name": "Frankfurt 1", "country": "DE"},
    "GRA": {"id": "GRA", "name": "Gravelines ", "country": "FR"},
    "GRA1": {"id": "GRA1", "name": "Gravelines 1", "country": "FR"},
    "GRA2": {"id": "GRA2", "name": "Gravelines 2", "country": "FR"},
    "GRA7": {"id": "GRA7", "name": "Gravelines 7", "country": "FR"},
    "GSW": {"id": "GSW", "name": "Paris GSW", "country": "FR"},
    "HIL1": {"id": "HIL1", "name": "Hillsboro, Oregon 1", "country": "US"},
    "LON1": {"id": "LON1", "name": "London 1", "country": "UK"},
    "P19": {"id": "P19", "name": "Paris P19", "country": "FR"},
     "RBX": {"id": "RBX", "name": "Roubaix ", "country": "FR"},
    "RBX1": {"id": "RBX1", "name": "Roubaix 1", "country": "FR"},
    "RBX2": {"id": "RBX2", "name": "Roubaix 2", "country": "FR"},
    "RBX3": {"id": "RBX3", "name": "Roubaix 3", "country": "FR"},
    "RBX4": {"id": "RBX4", "name": "Roubaix 4", "country": "FR"},
    "RBX5": {"id": "RBX5", "name": "Roubaix 5", "country": "FR"},
    "RBX6": {"id": "RBX6", "name": "Roubaix 6", "country": "FR"},
    "RBX7": {"id": "RBX7", "name": "Roubaix 7", "country": "FR"},
    "SBG": {"id": "SBG", "name": "Strasbourg ", "country": "FR"},
    "SBG1": {"id": "SBG1", "name": "Strasbourg 1", "country": "FR"},
    "SBG2": {"id": "SBG2", "name": "Strasbourg 2", "country": "FR"},
    "SBG3": {"id": "SBG3", "name": "Strasbourg 3", "country": "FR"},
    "SGP1": {"id": "SGP1", "name": "Singapore 1", "country": "SG"},
    "SYD1": {"id": "SYD1", "name": "Sydney 1", "country": "AU"},
    "VIN1": {"id": "VIN1", "name": "Vint Hill, Virginia 1", "country": "US"},
    "WAW1": {"id": "WAW1", "name": "Warsaw 1", "country": "PL"},
}


class BibindDriver(OvhNodeDriver):

    BIBINDLOCATIONS = BIBINDLOCATIONS
    def index_in_list(a_list, index):
        print(index < len(a_list))

    def _to_location(self, obj):
        location = self.BIBINDLOCATIONS[obj]
        return NodeLocation(driver=self, **location)



class ochcloud_bibind(object):
    

    
    def get_provider_cst(self):
        Ovh = get_driver('bibind')
        driver = Ovh('xUEdjyPkmNCJyRhl','YNexUap0BWHo0aWk5G3N8rA8QqMPocVy','407fc2f957624f9f8374cfb70b8fcfc9', 'JpSb8OESQDkifwmnC2rWJPtX85XKE2eH')
        for node in driver.list_locations():
            print(type(node))
 
    
    
    def create_user_gitlab(self):
        
        gl = gitlab.Gitlab('https://lab.bibind.com/', '3Kb2LjfCW-Qn1RLyTP2y', ssl_verify=False)
        gl.auth()
        
        
        p = gl.projects.create({'name': 'test_jojo_projet'}, sudo='jojodoi')
        print(p)
        
    
    
    def create_node(self):
        
        Ovh = get_driver('ovh')
        #driver = Ovh('aeNU3zwooBfui4hV','60XdgjYPnKDNgRHxpgVVgLB8DvQYK9g0','9521feabdf2241bda7b22a8b37197dec','8E0DJcWjpzQ45umYmZ28kb0FAl759MdP')
        driver = Ovh('xUEdjyPkmNCJyRhl','YNexUap0BWHo0aWk5G3N8rA8QqMPocVy','407fc2f957624f9f8374cfb70b8fcfc9', 'JpSb8OESQDkifwmnC2rWJPtX85XKE2eH')
        
        
        node = driver.ex_get_node('cccfddd1-59e5-4729-a29c-b919f02d04cc')   
        ip_address = node.public_ips
        SCRIPT = '''#!/usr/bin/env bash
                apt-get -y update && apt-get -y install curl
                '''
        
        step = ScriptDeployment(SCRIPT)
        msd = MultiStepDeployment([step])
        
        logger.info('+vimage  %s  ' %(driver) )
        SSH_CONNECT_TIMEOUT = 1 * 60
        ssh_timeout = 10 
        timeout = SSH_CONNECT_TIMEOUT
        max_tries = 3
        
        
        ssh_client = SSHClient(hostname=ip_address[0],
                               port=22, username='debian',
                               password='',
                               key_files='/var/lib/odoo/.ssh/id_rsa',
                               timeout=ssh_timeout)
        logger.info(ssh_client) 
        ssh_client.connect()
        logger.info(ssh_client)
        
        
        
        
    def destroy_node(self):
        for node in driver.list_nodes():
           if node.name=='vps-ssd-1':
               fin = driver.destroy_node(node)
               print('fin')
           else:
              print('ok')
              
              
    def list_favore_or_size(self):
        env = Environment(loader=PackageLoader('tests', './'))
        tmpl = env.get_template('docker-compose.yml.jinja2')

        result = tmpl.render(
             
             projetname=u"monsiteweb"
             
        )
        with open("docker-compose-dev.yml", "wb") as fh:
            fh.write(result)
            
    def populate_depot(self):
            
            
            DIRECTORY='id_clientname'
            GIT_PROJET='ssh://git@lab.bibind.com:10022/jojodoi/test_jojo_projet.git'
            APP_URL='https://ftp.drupal.org/files/projects/openatrium-7.x-2.615-core.tar.gz'
            APP_NAME='openatrium-7.x-2.615'
            PROJET_DIRECTORY='test_jojo_projet'
            cmd ='sh /mnt/extra-addons/bibind/models/depots/scripts/populate_depot.sh '+DIRECTORY+' '+GIT_PROJET+' '+APP_URL+' '+APP_NAME+' '+PROJET_DIRECTORY
            
            proc = subprocess.Popen([ cmd ],shell=True, close_fds=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            print(out)
            print(err)
            print(proc.returncode)
           




ochcloud_bibind()

a = ochcloud_bibind()


a.get_provider_cst()