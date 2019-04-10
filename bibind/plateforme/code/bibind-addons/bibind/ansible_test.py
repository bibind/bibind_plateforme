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

import os
import sys
import argparse

from collections import defaultdict


def get_template_paths():
       
        return [os.path.abspath(os.path.join(os.path.dirname(__file__)))]

    
def create_jinja_env():
        return Environment(
            loader=FileSystemLoader(
                get_template_paths()
            )
        )

def get_template(hosts):
        
        jinja_env = create_jinja_env()
        groups = hosts
        tmpl = 'inventory.jinj2'
        

        template = jinja_env.get_template(tmpl)
        result = template.render(
             
             groups=groups,
            
             
        )
        inventory = open('my_inventory.txt', 'w')
        inventory.write(result)
        inventory.close()

        return groups


def get_group(hosts):
    grp = {}
    ips ={}
        
    dd = defaultdict(list)
    
   
    
    
    for d , v in hosts.iteritems():
        for key, value in v.iteritems():
            dd[key].append(value)
        
    
        
    return dd

def get_hosts():
        hosts ={}
        hosts[4] = { 'mysql':'149.202.162.146'}
        hosts[5] = { 'mysql':'149.202.162.147'}
        hosts[6] = { 'web':'149.202.162.148'}
        hosts[7] = { 'web':'149.202.162.149'}
        hosts[8] = { 'web':{'children':['apache','varnish']}}
        return hosts
    
def get_inventory():
        hosts = get_hosts()
        
        list_group = get_group(hosts)
        
        inventory = get_template(list_group)
        
        print inventory
        
get_inventory()