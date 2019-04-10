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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time, os, random, string
from openerp import pooler
from openerp import models, fields, api, _
from openerp import pooler, tools
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import logging
from lxml import etree
import paramiko
from paramiko import SSHClient
import ovh

_logger = logging.getLogger("dedaluvia_cloudservice")


def password():
    length = 8
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))

class cloud_service (models.Model):
    _name = 'cloud.service'
    _description = 'cloud.service'
    
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
        'name':fields.Char('Name', size=128, required=True),
        'description':fields.Text('Description', required=True),
        'write_date': fields.Date(
            string='Last Modified on',
           ),
        'create_date': fields.Date(
            string='Created on',
        ),
        'state': fields.Selection([
            ('draft', 'Draft service'),
            ('cancel', 'annuler'),
            ('deactivate', 'désactiver'),
            ('waiting_date', 'Waiting Schedule'),
            ('progress', 'service en progression'),
            ('manual', 'Lancer manuellement la procedure de création du service'),
            ('done', 'Terminer'),
            ], 'Status', readonly=True, copy=False, help="Gives the status of the service cloud.\
              .", select=True),
         'expire_date': fields.Date(string='Date d\'expiration',
            help='This is the date where the service as expired.'),
        'alert_date': fields.Date(string='Alert Date',
            help="This is the date where le the customer would be alerted by the site ."),
    
        'partner_id' :fields.Many2one('res.partner', string='Partenaire', required=True),
        'fournisseur_id' :fields.Many2one('res.partner','Supplier',  required=True),
      
    }
    _defaults = {
    }
    _order = 'id'
    


class cloud_service_domain (models.Model):
    _name = 'cloud.service.domain'
    _inherit = 'cloud.service'
    _description = 'cloud.service.domain'

    def getFournisseurZoneDnsrecordId(self, cr, uid, ids, context):
            # create a client using configuration
            zonerecords ={}
            client = ovh.Client(endpoint='ovh-eu')
            # Request RO, /me API access
            access_rules = [
                           {'method': 'GET', 'path': '/*'},
                            {'method': 'POST', 'path': '/*'},
                             {'method': 'PUT', 'path': '/*'},
                              {'method': 'DELETE', 'path': '/*'},
                          
                            ]
            # Request token
            #validation = client.request_consumerkey(access_rules)
            for domain in self.browse(self, cr, uid, ids, context=None):
                zone = domain.domain
                _logger.info('zone   %s' % (zone))
       
            zone = '/domain/zone/'+zone
            zonerecords = client.get(zone)
            _logger.info('zone records  %s' % (zonerecords))
       
            return zonerecords
        
        
    def getFournisseurLineZoneDnsrecordById(self, cr, uid, ids, record, context=None):
            # create a client using configuration
            linerecordid ={}
            client = ovh.Client(endpoint='ovh-eu')
            # Request RO, /me API access
            access_rules = [
                           {'method': 'GET', 'path': '/*'},
                            {'method': 'POST', 'path': '/*'},
                             {'method': 'PUT', 'path': '/*'},
                              {'method': 'DELETE', 'path': '/*'},
                          
                            ]
            # Request token
            #validation = client.request_consumerkey(access_rules)
            for domain in self.browse(self, cr, uid, ids, context=None):
                zone = domain.domain
                _logger.info('zone   %s' % (zone))
       
            zone = '/domain/zone/'+zone+'/record/'+record
            linerecordid = client.get(zone)
            _logger.info('zone records  %s' % (linerecordid))
       
            return zonerecords
        
        
        
    def getLineZonednsByRecords(self, cr, uid, ids, context):
        
        Records = self.getFournisseurZoneDnsrecordId(cr, uid, ids, context)
        lines ={}
        for record in Records:
             try:
                 lines[record] = self.getFournisseurLineZoneDnsrecordById(self, cr, uid, ids, record, context)
             except IOError:
                 lines[record]=record
        
        return lines
              

    def checkDomainFournisseur(self, cr, uid, ids, context):
            for this in self.browse(cr, uid, ids, context):
                 _logger.info('this id  %s' % (this.id))
      
            # Request token
            #validation = client.request_consumerkey(access_rules)
            lines = getLineZonednsByRecords(self, cr, uid, ids, context)
            #text = "Please visit %s to authenticate" % validation['validationUrl']
                   # Print nice welcome message
            text2 = "Welcome , %s" % (lines)
            #text3 = "Btw, your 'consumerKey' is '%s'" % validation['consumerKey']
            s = "Description  avec ovh conf : %s " % (text2)
            self.write(cr, uid, ids, {'description': s}, context=context)
       
            return True

    def _getGestionDnsActivation(self, cr, uid, ids, fieldnames, args, context=None):
        
        result = {}
        for record in  self.browse(cr, uid, ids, context=context):
          result[record.id] = {
                record.id : 'Qui gere votre zone DNS',
            }
        return result

    _columns = {
        'domain' :fields.Char('Nom de domain', size=256, required=True),
        
        'gestion_dns_activation': fields.function(_getGestionDnsActivation, type='text', string='Gestion DNS',
        help="Service permettant de traduire votre nom de domain en adresse ip , ou la gestion de vos emails."),
       
        'dnssec': fields.Boolean(readonly=True, default=False, copy=False,
        help="Protection de la zone DNS du domain par authentifiaction."),
       
        'zone_dns_line': fields.One2many('cloud.service.domain.zonedns', 'service_domain_id', string='Zone DNS Lines',
        readonly=True)      
                }
    
class cloud_service_domain_zonedns(models.Model):
    _name = 'cloud.service.domain.zonedns'
    _description = 'cloud.service.domain.zonedns'
    
    _colums = {
        'service_domain_id':fields.Many2one('cloud.service.domain', string='Line Dns zone',
        ondelete='cascade', index=True),
    
        'zone_dns_domain':fields.Char('Domain', size=256, required=True),
        'zone_dns_ttl':fields.Char('TTL', size=256, required=True),
        'zone_dns_type':fields.Char('Type', size=256, required=True),
        'zone_dns_cible':fields.Char('Cible', size=256, required=True),
               
               }

class cloud_service_plateform (models.Model):
    _name = 'cloud.service.plateform'
    _inherit = 'cloud.service'
    _description = 'cloud.service.plateforme'
    _columns = {
        'ip' :fields.Char('', size=256, required=True),
        'Espace_disque':fields.Char('Name', size=256, required=True),
                
                }
    
    
class cloud_service_serveur (models.Model):
    _name = 'cloud.service.serveur'
    _inherit = 'cloud.service'
    _description = 'cloud.service.serveur'
    _columns = {
        'ip' :fields.Char('', size=256, required=True),
        'type':fields.Char('Name', size=256, required=True),
                
                }
    
    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
