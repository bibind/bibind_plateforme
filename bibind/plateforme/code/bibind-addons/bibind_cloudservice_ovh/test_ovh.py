## parser
from jinja2 import Environment, FileSystemLoader
import requests
import json
import ovh
import sys

class test_api(object):
    
    
      def get_bill(self):
        client = ovh.Client(endpoint='ovh-eu')
        zone = '/me/order/39335072/details/115772326'
        linerecordid = client.get(zone) 
        c =len( linerecordid)
        print c
        print linerecordid
        
        
      def verifDispo(self):
       
        client = ovh.Client(endpoint='ovh-eu')
            
        #for domain in self.browse( cr, uid, ids, context=None):
         #       zone = domain.domain

            #zone = 'order/domain/%s' %(zone)
        DOMAIN = "dedaloyat.com"
        duration = "12"
        OFFER = "PERFORMANCE_1"
        #o = "contact@example.com"
        zone = '/email/domain'
        linerecordid = client.get(zone)
      
         
        c =len( linerecordid)
        print c
        print linerecordid
        
          
      def get_domain(self):
        
          client = ovh.Client(endpoint='ovh-eu')
          zone = '/domain'
          linerecordid = client.get(zone)
          c =len( linerecordid)
          print c
          print linerecordid
          
      def get_zone(self):
        
          client = ovh.Client(endpoint='ovh-eu')
          zone = '/domain/zone'
          linerecordid = client.get(zone)
          c =len( linerecordid)
          print c
          print linerecordid
     
      def get_zone_zonename(self):
        
          client = ovh.Client(endpoint='ovh-eu')
          zone = '/order/domain/zone'
          linerecordid = client.get(zone)
          zone2 = '/order/domain/zone/dedaluvia.com'
          linerecordid2 = client.get(zone2)
          print 'zone 1 biot'
          c =len( linerecordid)
          print c
          print linerecordid
          print 'zone 2 dedal'
          c2 =len( linerecordid2)
          print c2
          print linerecordid2

          
      def get_plateforme(self):
        
          client = ovh.Client(endpoint='ovh-eu')
          zone = '/hosting/web/dedaluvia.com/serviceInfos'
          linerecordid = client.get(zone)
          c =len( linerecordid)
          print c
          print linerecordid
        

      def get_domain_servicename(self):
        
            url = 'https://eu.api.ovh.com/1.0'
            apijsonorder = requests.get(url).json()
            mes_model ={}
            for path in apijsonorder['apis']:
                
               
                modelurl=apijsonorder['basePath']+path['path']+"."+path['format'][0]
               
                model =requests.get(modelurl).json()
                
                for k,v in model['models'].items():
                    mes_model[k] = {}
                    mes_model[k]['name']= k
                    mes_model[k]['namespace'] =v['namespace']
                    mes_model[k]['description'] =v['description']
                    if k.endswith('Enum'):
                        mes_model[k]['field'] = {}
                        mes_model[k]['field'][v['id']] = {}
                        mes_model[k]['field'][v['id']]['name']=v['id']
                        
                        mes_model[k]['field'][v['id']]['ttype'] = 'selection'
                        mes_model[k]['field'][v['id']]['option'] = v['enum']
                    else:
                        mes_model[k]['field'] = {}
                        for m, j in v['properties'].items():
                            mes_model[k]['field'][m] = {}
                            mes_model[k]['field'][m]['name'] =m
                            mes_model[k]['field'][m]['ttype'] =j['type']
                            if j.has_key('fullType'):
                                mes_model[k]['field'][m]['ovhtype'] =j['fullType']
                            if j.has_key('description'):
                                mes_model[k]['field'][m]['help'] =j['description']

                    
                
                    
                break
            for b,n in mes_model.items():
                    print b
                    print n['field']
               
          #zone2 = '/domain/biotechinside.com'
          #linerecordid2 = client.get(zone2)
          
            #print apijsonorder
          
          



test_api()

a = test_api()


a.get_domain_servicename()

