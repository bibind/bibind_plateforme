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

from jinja2 import Environment, FileSystemLoader
import string
from pprint import pprint
import json
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

import os
import sys
import argparse

class BibindInventory(object):

    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.example_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.example_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.example_inventory()

        print json.dumps(self.inventory);

    # Example inventory for testing.
    def example_inventory(self):
        return {
            'locahost': {
                'server': ['149.202.162.146'],
                'vars': {},
                
            },
            '_meta': {
                'hostvars': {}
            }
        }

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

# Get the inventory.
BibindInventory()





class ResultCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """
    res = {}
    nodeid = {}
    tsk = {}
    nb = 0
    
    def v2_runner_item_on_ok(self, result):
        self.tsk.update({self.nb: result._result})
        self.nb = self.nb+1
        return self.tsk

    def v2_runner_item_on_failed(self, result):
        self.tsk.update({self.nb: result._result})
        self.nb = self.nb+1
        return self.tsk

    def v2_runner_item_on_skipped(self, result):
        self.tsk.update({self.nb: result._result})
        self.nb = self.nb+1
        return self.tsk

    def v2_runner_retry(self, result):
        self.tsk.update({self.nb: result._result})
        self.nb = self.nb+1
        return self.tsk
    
    def v2_runner_on_failed(self, result, ignore_errors=False):
        self.res = {self.nodeid: result._result}
        
        return self.res
    
    def v2_runner_on_unreachable(self, result):
        self.res = {self.nodeid: result._result}
        
        return self.res

    
    def v2_runner_on_ok(self, result, **kwargs):
        """Print a json represe#ntation of the result

        This method could store the result in an instance attribute for retrieval later
        """
        self.res = {self.nodeid: result._result}
        
        return self.res
    
        #print(json.dumps({host.name: result._result}, indent=4))
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

def get_template_paths():
       
        return [os.path.abspath(os.path.join(os.path.dirname(__file__)))]

    
def create_jinja_env():
        return Environment(
            loader=FileSystemLoader(
                get_template_paths()
            )
        )

def get_template():
        
        jinja_env = create_jinja_env()
        groups = {}
        adress_ips = {}
        adress_ips = {'149.202.162.146'}
        group = {'name':'server', 'adress_ips':adress_ips}
        
        groups['server']=group
        
         
        tmpl = 'inventory.jinj2'
        

        template = jinja_env.get_template(tmpl)
        result = template.render(
             
             groups=groups,
            
             
        )
        inventory = open('my_inventory.txt', 'w')
        inventory.write(result)
        inventory.close()

        return inventory


Options = namedtuple('Options', ['connection', 'module_path', 'forks', 'become', 'become_method', 'become_user', 'check', 'diff'])
# initialize needed objects
loader = DataLoader()
options = Options(connection='ssh', module_path='/usr/local/lib/python2.7/dist-packages/ansible', forks=100, become=None, become_method=None, become_user=None, check=False,
                  diff=False)
passwords = dict(vault_pass='secret')

# Instantiate our ResultCallback for handling results as they come in
results_callback = ResultCallback()
results_callback.nodeid ='my_id_node'
list = get_template()

# create inventory and pass to var manager
inventory =  InventoryManager(loader=loader, sources=['my_inventory.txt'])
variable_manager = VariableManager(loader=loader, inventory=inventory)

# create play with tasks


play_source = loader.load_from_file('/mnt/extra-addons/bibind/create_site_ovh.yml')[0]
play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

# actually run it
tqm = None
try:
    tqm = TaskQueueManager(
              inventory=inventory,
              variable_manager=variable_manager,
              loader=loader,
              options=options,
              passwords=passwords,
             stdout_callback=results_callback,# Use our custom callback instead of the ``default`` callback plugin
          )
    #print "test" 
    result = tqm.run(play)
    print results_callback.tsk
    
finally:
    if tqm is not None:
        tqm.cleanup()
        #print "finally"

