import Soapovh
import client
from .exceptions import (
    APIError, NetworkError, InvalidResponse, InvalidRegion, ReadOnlyError,
    ResourceNotFoundError, BadParametersError, ResourceConflictError, HTTPError,
    InvalidKey,
)
class test_api(object):
    
    
      def verifDispo(self):
       
        client = ovh.Client(endpoint='ovh-eu')
            
        #for domain in self.browse( cr, uid, ids, context=None):
         #       zone = domain.domain

            #zone = 'order/domain/%s' %(zone)
        DOMAIN = "dedaloyat.com"
        duration = "12"
        OFFER = "PERFORMANCE_1"
        #o = "contact@example.com"
        zone = '/domain/dedaluvia.com/serviceInfos'
        linerecordid = client.get(zone)
      
         
        
        print linerecordid
        


test_api()

a = test_api()

a.verifDispo()
  