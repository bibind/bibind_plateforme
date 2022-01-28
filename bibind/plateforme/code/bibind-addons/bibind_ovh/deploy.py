#!/usr/bin/env python
from pprint import pprint
import requests
import json
import ovh
import sys
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

# rancher 
# cle acces
# 5B8D466780146E519CA7 
# Cle secrete (mot de passe)
# frWiggMWWCb2CeZVvLr5uqzS6KgAYLRWS96kF8sB 

# Ovh = get_driver(Provider.OVH)
# #driver = Ovh('aeNU3zwooBfui4hV','60XdgjYPnKDNgRHxpgVVgLB8DvQYK9g0','9521feabdf2241bda7b22a8b37197dec','8E0DJcWjpzQ45umYmZ28kb0FAl759MdP')
# driver = Ovh('xUEdjyPkmNCJyRhl','YNexUap0BWHo0aWk5G3N8rA8QqMPocVy','9521feabdf2241bda7b22a8b37197dec', 'JpSb8OESQDkifwmnC2rWJPtX85XKE2eH')
# nodes = driver.list_nodes()
# bca503d8e6f8244e90293e7d603cad859565871a
# for n in nodes:
#    id = driver.ex_get_node(n)
#    pprint(id)
class test_api(object):
    
    
      def get_cloud(self):
        client = ovh.Client(endpoint='ovh-eu')
        zone = '/cloud/project/9521feabdf2241bda7b22a8b37197dec/flavor/'
        params ={}
        params['flavorId'] = 'b5f8044d-c108-4d83-abca-f1a2f5b922f2'
        linerecordid = client.get(zone) 
        
        print linerecordid
        
test_api()

a = test_api()


a.get_cloud()


