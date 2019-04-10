import time
import pprint
import json
import SOAPpy
from SOAPpy import WSDL





class api_ovh(object):
    """api old ovh pour check domain"""
    #soap = WSDL.Proxy('https://www.ovh.com/soapi/soapi-re-1.63.wsdl')
    
    
    def domain_check(self, domain):
        
        
        #domainCheck
        session = self.soap.login('ha6877-ovh', 'Dedalehvin44', 'fr', 0)
        result = self.soap.domainCheck(session, domain)
        #logout

        pp = pprint.PrettyPrinter(indent=4)
        rs=SOAPpy.Types.simplify(result)
        h = {}
        k = 0
        for key in rs['item']:
            h[key['predicate']]=key['value']
            k =k+1
        
        return h

api_ovh()
            
    

