from jinja2 import Environment, FileSystemLoader
import ovh
import re
import logging
import erppeek


class test_api(object):
    
    
      def get_bill(self):
        #client = ovh.Client(endpoint='ovh-eu')
        #zone = '/me/order/28630053/associatedObject'
        #linerecordid = client.get(zone) 
        #c =len( linerecordid)
        #print c
        p ={}
        p['domaine']='mondomain.com'
        p['duration']='12'
        p['orderId']='568456'
        p['un autre']='mondomjjjain.com'
        
        logging.basicConfig(level=logging.DEBUG)
        logging.debug('This message should go to the log file')
        
        texte ='/me/order/{orderId}/details/{un autre}'
        reste = {}
        for k in p:
            
            if texte.find(k)!=-1:
                texte = texte.replace('{'+k+'}', p[k])
            else :
               
                reste[k]=p[k]
        
        print texte
        print reste
        
        print texte.find('{')
        
        begin_balise = '{'
        end_balise = '}'
        motif = begin_balise + '.*' + end_balise
        obj_regex = re.search(motif, texte)
        logging.debug('test %s' %(obj_regex))
         
        if obj_regex is None:
            print "Pas de titre reconnaissable dans le fichier."
        else:
            texte = obj_regex.group()
            texte = texte.replace(begin_balise, '')
            texte = texte.replace(end_balise, '')
           
        print "Voici le titre :", texte
        
      def create_service(self):
          p ={}
          p['domain'] ="domain"
          ''
          t ='create_domain'
          func = getattr(self, t)
          res = func()
          
          print res
        
      def create_domain(self):
          
          return "creation ddd domain"
      
      def create_hebergement(self):
          
          return "creation hebergement"
        
      def verifDispo(self):
       
        client = ovh.Client(endpoint='ovh-eu')
            
        #for domain in self.browse( cr, uid, ids, context=None):
         #       zone = domain.domain

            #zone = 'order/domain/%s' %(zone)
        DOMAIN = "dedaloyat.com"
        duration = "12"
        OFFER = "PERFORMANCE_1"
        #o = "contact@example.com"
        zone = '/order/hosting/web/new'
        p = {}
        p['domain']='dedaluvia.com'
        p['offer']='PRO'
        print p
        linerecordid = client.get(zone, **p)
      
         
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
        
          client = ovh.Client(endpoint='ovh-eu')
          zone = '/domain/dedaluvia.com/serviceInfos'
          linerecordid = client.get(zone)
          
          #zone2 = '/domain/biotechinside.com'
          #linerecordid2 = client.get(zone2)
          print 'domain 1'
          c =len( linerecordid)
          print c
          print linerecordid
          
          
      def test_erp(self):
          
          api = erppeek.Client('http://91.121.79.171:8069','bibind_db','admin','bibind@74')
          print api.common.version()
          u    =    api.model('res.users').browse([])
          print u.name
          m    =    api.model('cloud.service.api.bibind').browse([])
          print m.name
          



test_api()

a = test_api()


a.test_erp()

