import os
import pprint
import json





class soapi_ovh(object):
    
        
    def get_path(self):
        print os.path.split(os.path.realpath(__file__))[0]+"/ovh.conf"

soapi_ovh()

a = soapi_ovh()


a.get_path()
