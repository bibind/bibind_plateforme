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


import gitlab
from jinja2 import Environment, PackageLoader


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





class ochcloud_bibind(object):
    
    DRIVERS = {
    Provider.AZURE:
    ('libcloud.compute.drivers.azure', 'AzureNodeDriver'),
    Provider.AZURE_ARM:
    ('libcloud.compute.drivers.azure_arm', 'AzureNodeDriver'),
    Provider.DUMMY:
    ('libcloud.compute.drivers.dummy', 'DummyNodeDriver'),
    Provider.EC2:
    ('libcloud.compute.drivers.ec2', 'EC2NodeDriver'),
    Provider.ECP:
    ('libcloud.compute.drivers.ecp', 'ECPNodeDriver'),
    Provider.ELASTICHOSTS:
    ('libcloud.compute.drivers.elastichosts', 'ElasticHostsNodeDriver'),
    Provider.SKALICLOUD:
    ('libcloud.compute.drivers.skalicloud', 'SkaliCloudNodeDriver'),
    Provider.SERVERLOVE:
    ('libcloud.compute.drivers.serverlove', 'ServerLoveNodeDriver'),
    Provider.CLOUDSIGMA:
    ('libcloud.compute.drivers.cloudsigma', 'CloudSigmaNodeDriver'),
    Provider.GCE:
    ('libcloud.compute.drivers.gce', 'GCENodeDriver'),
    Provider.GOGRID:
    ('libcloud.compute.drivers.gogrid', 'GoGridNodeDriver'),
    Provider.RACKSPACE:
    ('libcloud.compute.drivers.rackspace', 'RackspaceNodeDriver'),
    Provider.RACKSPACE_FIRST_GEN:
    ('libcloud.compute.drivers.rackspace', 'RackspaceFirstGenNodeDriver'),
    Provider.KILI:
    ('libcloud.compute.drivers.kili', 'KiliCloudNodeDriver'),
    Provider.VPSNET:
    ('libcloud.compute.drivers.vpsnet', 'VPSNetNodeDriver'),
    Provider.LINODE:
    ('libcloud.compute.drivers.linode', 'LinodeNodeDriver'),
    Provider.RIMUHOSTING:
    ('libcloud.compute.drivers.rimuhosting', 'RimuHostingNodeDriver'),
    Provider.VOXEL:
    ('libcloud.compute.drivers.voxel', 'VoxelNodeDriver'),
    Provider.SOFTLAYER:
    ('libcloud.compute.drivers.softlayer', 'SoftLayerNodeDriver'),
    Provider.EUCALYPTUS:
    ('libcloud.compute.drivers.ec2', 'EucNodeDriver'),
    Provider.OPENNEBULA:
    ('libcloud.compute.drivers.opennebula', 'OpenNebulaNodeDriver'),
    Provider.BRIGHTBOX:
    ('libcloud.compute.drivers.brightbox', 'BrightboxNodeDriver'),
    Provider.NIMBUS:
    ('libcloud.compute.drivers.ec2', 'NimbusNodeDriver'),
    Provider.BLUEBOX:
    ('libcloud.compute.drivers.bluebox', 'BlueboxNodeDriver'),
    Provider.GANDI:
    ('libcloud.compute.drivers.gandi', 'GandiNodeDriver'),
    Provider.DIMENSIONDATA:
    ('libcloud.compute.drivers.dimensiondata', 'DimensionDataNodeDriver'),
    Provider.OPENSTACK:
    ('libcloud.compute.drivers.openstack', 'OpenStackNodeDriver'),
    Provider.VCLOUD:
    ('libcloud.compute.drivers.vcloud', 'VCloudNodeDriver'),
    Provider.TERREMARK:
    ('libcloud.compute.drivers.vcloud', 'TerremarkDriver'),
    Provider.CLOUDSTACK:
    ('libcloud.compute.drivers.cloudstack', 'CloudStackNodeDriver'),
    Provider.LIBVIRT:
    ('libcloud.compute.drivers.libvirt_driver', 'LibvirtNodeDriver'),
    Provider.JOYENT:
    ('libcloud.compute.drivers.joyent', 'JoyentNodeDriver'),
    Provider.VCL:
    ('libcloud.compute.drivers.vcl', 'VCLNodeDriver'),
    Provider.KTUCLOUD:
    ('libcloud.compute.drivers.ktucloud', 'KTUCloudNodeDriver'),
    Provider.HOSTVIRTUAL:
    ('libcloud.compute.drivers.hostvirtual', 'HostVirtualNodeDriver'),
    Provider.ABIQUO:
    ('libcloud.compute.drivers.abiquo', 'AbiquoNodeDriver'),
    Provider.DIGITAL_OCEAN:
    ('libcloud.compute.drivers.digitalocean', 'DigitalOceanNodeDriver'),
    Provider.NEPHOSCALE:
    ('libcloud.compute.drivers.nephoscale', 'NephoscaleNodeDriver'),
    Provider.EXOSCALE:
    ('libcloud.compute.drivers.exoscale', 'ExoscaleNodeDriver'),
    Provider.IKOULA:
    ('libcloud.compute.drivers.ikoula', 'IkoulaNodeDriver'),
    Provider.OUTSCALE_SAS:
    ('libcloud.compute.drivers.ec2', 'OutscaleSASNodeDriver'),
    Provider.OUTSCALE_INC:
    ('libcloud.compute.drivers.ec2', 'OutscaleINCNodeDriver'),
    Provider.VSPHERE:
    ('libcloud.compute.drivers.vsphere', 'VSphereNodeDriver'),
    Provider.PROFIT_BRICKS:
    ('libcloud.compute.drivers.profitbricks', 'ProfitBricksNodeDriver'),
    Provider.VULTR:
    ('libcloud.compute.drivers.vultr', 'VultrNodeDriver'),
    Provider.AURORACOMPUTE:
    ('libcloud.compute.drivers.auroracompute', 'AuroraComputeNodeDriver'),
    Provider.CLOUDWATT:
    ('libcloud.compute.drivers.cloudwatt', 'CloudwattNodeDriver'),
    Provider.PACKET:
    ('libcloud.compute.drivers.packet', 'PacketNodeDriver'),
    Provider.ONAPP:
    ('libcloud.compute.drivers.onapp', 'OnAppNodeDriver'),
    Provider.OVH:
    ('libcloud.compute.drivers.ovh', 'OvhNodeDriver'),
    Provider.INTERNETSOLUTIONS:
    ('libcloud.compute.drivers.internetsolutions',
     'InternetSolutionsNodeDriver'),
    Provider.INDOSAT:
    ('libcloud.compute.drivers.indosat', 'IndosatNodeDriver'),
    Provider.MEDONE:
    ('libcloud.compute.drivers.medone', 'MedOneNodeDriver'),
    Provider.BSNL:
    ('libcloud.compute.drivers.bsnl', 'BSNLNodeDriver'),
    Provider.NTTA:
    ('libcloud.compute.drivers.ntta', 'NTTAmericaNodeDriver'),
    Provider.ALIYUN_ECS:
    ('libcloud.compute.drivers.ecs', 'ECSDriver'),
    Provider.CLOUDSCALE:
    ('libcloud.compute.drivers.cloudscale', 'CloudscaleNodeDriver'),
}
    
    def get_provider_cst(self):
       
        
        Ovh = get_driver('ovh')
        driver = Ovh('xUEdjyPkmNCJyRhl','YNexUap0BWHo0aWk5G3N8rA8QqMPocVy','9521feabdf2241bda7b22a8b37197dec', 'JpSb8OESQDkifwmnC2rWJPtX85XKE2eH')
        for node in driver.list_nodes():
            print node.state
 
    
    
    def create_user_gitlab(self):
        
        gl = gitlab.Gitlab('https://lab.bibind.com/', '3Kb2LjfCW-Qn1RLyTP2y', ssl_verify=False)
        gl.auth()
        
        
        p = gl.projects.create({'name': 'test_jojo_projet'}, sudo='jojodoi')
        print p
        
    
    
    def create_node(self):
        
        Ovh = get_driver('libbibind')
        #driver = Ovh('aeNU3zwooBfui4hV','60XdgjYPnKDNgRHxpgVVgLB8DvQYK9g0','9521feabdf2241bda7b22a8b37197dec','8E0DJcWjpzQ45umYmZ28kb0FAl759MdP')
        driver = Ovh('xUEdjyPkmNCJyRhl','YNexUap0BWHo0aWk5G3N8rA8QqMPocVy','9521feabdf2241bda7b22a8b37197dec', 'JpSb8OESQDkifwmnC2rWJPtX85XKE2eH')
        
        
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
               print 'fin'
           else:
              print 'ok'
              
              
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
            print out
            print err 
            print proc.returncode
           




ochcloud_bibind()

a = ochcloud_bibind()


a.populate_depot()