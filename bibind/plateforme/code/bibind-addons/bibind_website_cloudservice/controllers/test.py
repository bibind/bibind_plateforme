import simplejson as json
import xml.etree.ElementTree as ET
from ovh import api_ovh


class parse:
    
    
    def check_parse(self):
        tree = ET.parse('extension.xml')
        root = tree.getroot()
        data ={}
        data['current'] = 1
        data['rowCount'] = 10
        data['rows'] = []
        k = 0
        for child in root:
            data['rows'].append({'id':k,'did': int(child.attrib.get('id')),'etat':'','price': child.attrib.get('price'),'categorie': child.attrib.get('categorie'), 'domain': 'mondodod.'+child.attrib.get('extension'),'extension':child.attrib.get('extension')})
            k = k+1
        
        data['total'] = k
        with open('/opt/recette_odoo-addons/dedaluvia_website_checkout/controllers/dataAll-01.json', 'w') as f:
            json.dump(data, f, ensure_ascii=False)
        
        print json.dumps(data)
       
    def check_json(self):
        with open('/opt/recette_odoo-addons/dedaluvia_website_checkout/controllers/data.json') as data_file:    
            data = json.load(data_file)
        
        for key in data['rows'] :
            key['domain'] = 'mondomain.'+key['domain']
        
        print data
        
    def check_available(self, domain, rowid):
        apiovh = api_ovh()
        data ={}
        data['rowid']=rowid
        check = apiovh.domain_check(domain)
        data['check']= check
        data = json.dumps(data)
        print data
        
a = parse()

a.check_parse()
