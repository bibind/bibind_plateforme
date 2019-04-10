# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 ASPerience SARL (<http://www.asperience.fr>).
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#Domaine ovh api 

############################################################################







from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time, os, random, string
from openerp import pooler
from openerp import SUPERUSER_ID

from openerp.osv import fields, osv

from openerp import pooler, tools
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
import json
import re
from lxml import etree
import paramiko
from paramiko import SSHClient
import ovh

from socket import getaddrinfo

_logger = logging.getLogger("bibind_cloudservice")


def password():
    length = 8
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))

class cloud_service_ovh_me (osv.osv):
    _name = 'cloud.service.ovh.me'
    _description = 'cloud.service.ovh.me'
    
    def onchange_partner_id(self, cr, uid, ids, part, context=None):
        
        return True
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result
    
    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)


    _columns = {
        'name':fields.char('Name', size=128 ),
        'nichandle':fields.char('nichandle', size=128 ),
        'sex':fields.char('Sexe', size=128 ),
        'ovhCompany':fields.char('ovhCompany', size=128 ),
        'prenom':fields.char('prÃ©nom', size=128 ),
        'nom':fields.char('Nom', size=128 ),
        'area':fields.char('Area', size=128 ),
        'forme_juridique':fields.char('Form juridique', size=128 ),
        'organisation':fields.char('Organisation', size=128 ),
        'tax_eu_id':fields.char('EU Tax ID', size=128 ),
        'nichandle':fields.char('Nichandle', size=128 ),
        'adresse':fields.char('Adresse', size=128 ),
        'code_postal':fields.char('Code Postal', size=128 ),
        'ville':fields.char('Ville', size=128 ),
        'pays':fields.char('Pays', size=128 ),
        'tel':fields.char('TÃ©lÃ©phone', size=128 ),
        'fax':fields.char('Fax', size=128 ),
        'email':fields.char('Email', size=128 ),
        'email_2':fields.char('Email de secour', size=128 ),
        'companyNationalIdentificationNumber':fields.char('companyNationalIdentificationNumber', size=128 ),
        'state':fields.char('state', size=128 ),
        'language':fields.char('language', size=128 ),
        'description':fields.text('Description'),
        'write_date': fields.datetime(
            'Last Modified on',
            select=True, readonly=True,
        ),
        'create_date': fields.datetime(
            'Created on',
            select=True, readonly=True,
        ),
        
    }
    _defaults = {
    }
    _order = 'id'
    
    def getMe(self, cr, uid, ids, context=None):
        """ se crÃ©er Ã  ovh pour voir la disponibilitÃ© de command  """
        client = ovh.Client(endpoint='ovh-eu')
            
        
        zone ='/me'
        me = client.get(zone)
        values = {}
        values['nichandle']=me['nichandle']
        values['ovhCompany']=me['ovhCompany']
        values['sex']= me['sex']
        values['nom']= me['name']
        values['prenom']=me['firstname']
        values['forme_juridique']=me['legalform']
        values['organisation']=me['organisation']
        values['tax_eu_id']=me['vat']
        values['adresse']=me['address']
        values['code_postal']=me['zip']
        values['ville']=me['city']
        values['pays']=me['country']
        values['area'] =me['area']
        values['tel']=me['phone']
        values['email']=me['email']
        values['fax']=me['fax']
        values['email_2']=me['spareEmail']
        values['companyNationalIdentificationNumber']=me['companyNationalIdentificationNumber']
        values['state']=me['state']
        values['language']=me['language']
        
        _logger.info('vale zoneid   %s' % (me))
        self.write(cr, uid, ids, values, context=context)
       
        
        return True
    
    
    
    
cloud_service_ovh_me()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
