# -*- encoding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
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
from odoo import SUPERUSER_ID

from odoo.exceptions import Warning
from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.osv.expression import get_unaccent_wrapper
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import odoo.addons.decimal_precision as dp
from odoo import netsvc
import logging
import json
import re
from lxml import etree
import paramiko
from paramiko import SSHClient

from socket import getaddrinfo
from pygments.lexer import _inherit


import gitlab

_logger = logging.getLogger("bibind_cloudservice")


class cloud_service(models.Model):
        _name = 'cloud.service'
        _inherit = ['mail.thread']
        _description = 'Cloud service'
   
   
        @api.model
        def projetname_search(self, name, args=None, operator='ilike', limit=100):
            args = args or []
            recs = self.browse()
            if name:
                recs = self.search([('projetname', '=', name)] + args, limit=limit)
                return recs
            else:
                return True


        def create_depot(self):
            
            glitlab_username = self.bibind_user_id.gitlab_username
            gl = gitlab.Gitlab('https://lab.bibind.com/', '3Kb2LjfCW-Qn1RLyTP2y', ssl_verify=False)
            gl.auth()

            p = gl.projects.create({'name': self.name}, sudo=glitlab_username)
            projet_vals = {}
            projet_vals = {
                'ssh_url' : p.ssh_url,
                'http_url' : p.http_url,
                'projet_name' : p.name,
                'runner_token' : p.runner_token,
                'gitlab_web_url' : p.web_url
                }
            depot = self.env['bibind.depot']
            depotid = depot.create(projet_vals)
            if depotid:
                self.depot_id = depotid.id
                self.depot_is_created = True;
                return self.depot_id
            else:
                return False
        
        def prepare_service(self):
            if self.depot_is_created:
            
                self.create_stack()
            
            else:
                return False
            
            return False
        
        def create_stack(self):
            api = self.cloud_service_environnement_id.api



        def _defaut_env(self):
            _logger.info('!!!!!!!id environnement : %s' % (self.cloud_service_environnement_id))
  
            if self.cloud_service_environnement_id != False:
                return True
            else:
                return False
   
   
        name = fields.Char(string='name', size=128, default='/')
        
        projetname = fields.Char(string='Service name', size=128, default='/')
        
        expire_date = fields.Datetime(string='Date d\'expiration',
            help='This is the date where the service as expired.')
        
        alert_date = fields.Datetime(string='Alert Date',
            help="This is the date where le the customer would be alerted by the site .")
        
        
        partner_id = fields.Many2one('res.partner', string='Client', required=True, default=lambda self: self.env.user.partner_id)
        
        bibind_user_id = fields.Many2one('bibind.user' , string='client ou utilisteur bibind')
        
        depot_id = fields.Many2one('bibind.depot', string='Depot du service')
        
        depot_is_created = fields.Boolean(string="status du depot (créer ou pas)")
        
        providerdriverid = fields.Many2many('res.partner', string='Provider driver machine')
       
       
        archi_id = fields.Many2one('cloud.service.archi', string='Provider')
       

       
        cloud_service_tmpl_id = fields.Many2one('cloud.service.tmpl', string='Template du service', help='Template qui a configurer le service')
        
        type_service = fields.Selection(selection=([
                                                    ('domain', 'Service domain'),
                                                    ('mutualise', 'MutualisÃ©'),
                                                    ('dedie_mutualise', 'DÃ©diÃ© MutualisÃ©'),
                                                    ('vm_mutualise', 'Virtual Machine pour MutualisÃ©'),
                                                    ('dedie', 'Serveur dÃ©diÃ©'),
                                                    ('vm', 'Machine virtuel'),
                                                    ('infrastructure', 'infrastructure'),
                                                    ]))
        
        Type_renew = fields.Many2one('cloud.service.renew.type', 'Type de renouvellement', help='Type de reouvellement du service (automatique, manuel)')
        
        cloud_service_fournisseur_id = fields.Many2one('cloud.service.fournisseur', 'service fournisseur')
        
        is_domain = fields.Boolean('Is domain service')
        
        is_active = fields.Boolean('Status du service', default=False)
          
        domain = fields.Char('Nom de domain')
        
        is_depend_domain = fields.Boolean('Ce service depend d un domain')
        
        domain_main = fields.Char('Domain principal')
        
        instance_service = fields.Reference(selection=[('cloud.service.instance.service', 'bibind instance service')])
        
        state = fields.Selection([('Provider', 'Choisir son provider'), ('environnement', 'Configurer son environnement'), ('application', 'Choisir son application'), ('dns_domain', 'Definir un Domain ou Zone DNS'), ('Piloter', ' Piloter son projet'), ('en_attente_service_fournisseur', 'en attente d\'un service fournisseur'), ('en_creation', 'en creation'), ('active', 'activÃ©'), ('expired', 'expirÃ©'), ('desactive', 'dÃ©sactivÃ©')]  , default='Provider')
        
        product_id = fields.Many2one('product.template')
        
        application = fields.Many2one('bibind.application', string='Appliquation')


        cloud_service_environnement_id = fields.One2many('cloud.service.environnement', 'cloudserviceid', string='Cloud Service Environnement')
  
        is_env = fields.Boolean('check envi', default=_defaut_env)
        # param_host=fields.Many2one()

        @api.model
        def get_environnement(self, context):
              
              _logger.info('*******id environnement : %s' % (self.cloud_service_environnement_id))
             # return view
              return {
                    'name':'Environemment',
                    'context': self.env.context,
                    'type': 'ir.actions.act_window',
                    'res_model': 'cloud.service.environnement',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [(False, 'form')],
                    'res_id': self.cloud_service_environnement_id.id,
                    'target': 'inline',
                     }
        
        
        @api.onchange('is_env')
        def _checkEnv(self):
            _logger.info('on changeid environnement : %s' % (self.cloud_service_environnement_id))
  
            if self.cloud_service_environnement_id != False:
                self.is_env = True
            else:
                self.is_env = False
        
        
        
       
    

        @api.constrains('cloud_service_fournisseur_id')
        def _check_service_limit(self):
            if self.cloud_service_fournisseur_id.availaible_service < 0:
                    raise Warning(_('No more available service for this service fournisseur .'))
        
        
        def get_service_fournisseur(self):
            if not self.cloud_service_fournisseur_id:
                tmpl = self.cloud_service_tmpl_id
                sf_tmpl = tmpl.tmpl_fournisseur_id
                
                service_type = self.type_service
                search_domain = []
                search_domain += ['type_service', '=', service_type]
                search_domain += ['available_service', '>', 0]
                              
                if self.is_domain and self.domain:
                    nom_de_domain = self.domain
                    search_domain += ['domain', '=', domain]
                              
                if self.is_depend_domain and self.domain_main:
                    nom_de_domain_main = self.domain_main
                    search_domain += ['domain_main', '=', nom_de_domain_main]
                              
                sf = self.env['cloud.servise.fournisseur'].search(search_domain)
                if sf:
                    self.write({'cloud_service_fournisseur_id':sf, 'state':'en_creation'})
                    
                    return sf
                else :
                    self.state = 'en_attente_service_fournisseur'
                    return False
            else :
                return self.cloud_service_fournisseur_id
            
            
        def configuration_service_by_service_fournisseur(self):
            if self.cloud_service_fournisseur_id:
                param_host = self.cloud_service_fournisseur_id.configure_service_client(self.id)
                if param_host['host']:
                    val = {
                           'service_id': self.id,
                           'name':self.name + '-param host',
                           'param_json_data':json.dumps(param_host),
                           'host_ipv4':param_host['ipv4'],
                           'host_ipv6':param_host['ipv6'],
                           'hostname':param_host['hostname'],
                           'user_name':param_host['user'],
                           'host_path':param_host['root_path'],
                           'password': param_host['password'],
                           
                          }
                    if param_host['db_host']:
                        val.update({
                                    'db_host': param_host['db_host'],
                                   'db_name': param_host['db_name'],
                                   'db_user':param_host['db_user'],
                                   'db_password':param_host['db_pass'],
                                    })
                    self.param_host_state = param_host['status']
                    param_host_ids = self.env['cloud.service.host.param'].create(val)
                    self.state = 'parametre_host'
                    return param_host_ids
                else :
                    self.param_host_state = 'en_attente'
                    return False
                
        def assign_model_manager_au_service(self): 
            if self.cloud_service_tmpl_id:
                self.instance_service = self.cloud_service_tmpl_id.instance_de_gestion
                
            
        def is_expired(self) :
            # returns 
            return
        
        @api.model
        def choose_provider(self):
            
            if  self.provider_id:
                 providerid = self.provider_id
            else :
                providerid = False
            
            self = self.with_context({'service_id':self.id, 'res_id':self.id, 'name':self.name, 'provider_id':providerid.id})
           
            
            return {
            'type': 'ir.actions.act_window',
            'res_model': 'services.builder',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': self.env.context
             }
        
        def choose_environnement(self):
            
            return
            
        def launch_renew(self):
            sale_order = self.env['sale.order']
            sale_order_line = self.env['sale.order.line']
            product = self.product_id
            val_sale_order_line = {
                                   'product_id': product,
                                   'cloud_service_id':self.id,
                                   'cloud_service_type':'renew'
                                   }
            sol = sale_order_line.create(val_sale_order_line)
            val_so = {
                      'sale_order_line':sol,
                      'cloud_service_type':'renew'
                      }
            so = sale_order.create(val_so)
            
        
        
        def desactiver(self) :
            # returns 
            return
        
        @api.model
        def activer(self) :
            # returns 
            return 
        def create_service(self) :
            # returns 
            return
        
        def supprimer_service(self) :
            # returns 
            return
        def get_api(self) :
            # returns 
            return
        
        
        def lancer_creation_depot(self, cr, uid, ids):
            client = SSHClient()    
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())   
            client.connect(this.manager_id.ip, username=this.manager_id.login, password=this.manager_id.password)
            stdin, stdout, stderr = client.exec_command('ls /opt/queue/out')
            res = stdout.read()
            for f in res.split('\n'): 
                if not f : 
                    continue 
                if f == this.code:
                    stdin, stdout, stderr = client.exec_command('cat /opt/queue/out/%s' % (f,))
                    res = stdout.read()
                    print(res)
                    client.exec_command('mv /opt/queue/out/%s /opt/queue/out/ok/' % (f,))
        
        
        
        def lancer_application(self, cr, uid, ids) :
            # returns 
            return
        
        def view_manager_service(self, cr, uid, ids) :
            # returns 
            return
        
        def cron_cheik_expired_service(self) :
            # returns 
            return
        
        def send_email_new_service(self) :
            email_templates = self.pool.get('email.template')
            template_ids = email_templates.search([('name', '=', 'template_new_service')])
            object = self
            if template_ids:
                email_templates.send_mail(template_ids[0], object.id, True)
            # returns 
            return
        
        def send_email_services_expired(self) :
            # returns 
            email_templates = self.pool.get('email.template')
            template_ids = email_templates.search([('name', '=', 'template_expired')])

            if template_ids:
                email_templates.send_mail(template_ids[0], object.id, True)
            
            return
        
        def send_email_service_suspendu_unpaid(self) :
            # returns 
            email_templates = self.pool.get('email.template')
            template_ids = email_templates.search([('name', '=', 'template_service_unpaid')])

            if template_ids:
                email_templates.send_mail(template_ids[0], object.id, True)
            
            return
        
        def send_email_reouverture_service(self) :
            # returns 
            email_templates = self.pool.get('email.template')
            template_ids = email_templates.search([('name', '=', 'template_service_reouverture')])

            if template_ids:
                email_templates.send_mail(template_ids[0], object.id, True)
            
            return
        
        def send_email_suppression_service(self) :
            # returns 
            email_templates = self.pool.get('email.template')
            template_ids = email_templates.search([('name', '=', 'template_suppression_service')])

            if template_ids:
                email_templates.send_mail(template_ids[0], object.id, True)
            
            return
        
        def suspendre_service(self) :
            # returns 
            return
        
        def sauvergaarder_service(self) :
            # returns 
            return
        
        def send_email_alert_expired_service(self) :
            # returns
            return
        
        def compute_default_value(self):
            return self.get_value()
        
        @api.model
        def create(self, vals) :
            # returns 
           
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].sudo().get('cloud.service') or '/'
          
            new_id = super(cloud_service, self).create(vals)

            return new_id
        
        
         
cloud_service()


class Cloud_Service_archi(models.Model):
        _name = 'cloud.service.archi'
        
        name = fields.Char(string='name', size=128, default='/')
        provider_id = fields.Many2one('res.partner', string='Provider')


Cloud_Service_archi()

class Cloud_Service_environnement(models.Model):
        _name = 'cloud.service.environnement'
        
        
        
        
        
        
        
        name = fields.Char(string='name', size=128)
        cloudserviceid = fields.Many2one('cloud.service', string="service client")
        dev_env = fields.One2many('cloud.service.environnement.dev', 'environnement_id', limit=1)
        test_env = fields.One2many('cloud.service.environnement.test', 'environnement_id', limit=1)
        live_env = fields.One2many('cloud.service.environnement.live', 'environnement_id', limit=1)
        branch_env = fields.One2many('cloud.service.environnement.branch', 'environnement_id', limit=10)
    
    
        @api.model
        def create(self, vals) :
            # returns 
            # _logger.info('++++++id environnement context service env : %s' % (self.cloudserviceid.id))
            _logger.info('++++++id environnement valsv : %s' % (vals.get('cloudserviceid')))
  
            if vals.get('cloudserviceid'):
                s = self.env['cloud.service'].browse(vals.get('cloudserviceid'))
              
                vals['name'] = (_(" env_%s ") % (s.name)) or '/env_test'
          
            new_id = super(Cloud_Service_environnement, self).create(vals)
            return new_id
        
        
        
        
        
        @api.model
        def backup_dev(self):
            return {'value':{}, 'warning':{'title':'warning', 'message':'Your message'}}
        


Cloud_Service_environnement()

class Cloud_Service_environnement_test(models.Model):
        _name = 'cloud.service.environnement.test'
   
        environnement_id = fields.Many2one('cloud.service.environnement')
        service_param_host_git = fields.Text('parametre host pour git')  
        service_param_host_db = fields.Text('parametre host db  ')  
        service_param_host = fields.Text('parametre host sftp ')  
        branche_id = fields.Char('Branche')
        tag_id = fields.Char('tag')
        git_ref_id = fields.Char('Ref commit last')
        application_name = fields.Char('Nom de Application')
       
        
Cloud_Service_environnement_test()

class Cloud_Service_environnement_dev(models.Model):
        _name = 'cloud.service.environnement.dev'
   
        state = fields.Selection(selection=[('deactivate', 'dÃ©sactivÃ©'), ('activate', 'activÃ©')])
        name = fields.Char('Name')
        service_param_host_git = fields.Text('parametre host pour git json')  
        service_param_host_db = fields.Text('parametre host db  json')  
        service_param_host = fields.Text('parametre host sftp json')  
        branche_id = fields.Char('Branche')
        tag_id = fields.Char('tag')
        git_ref_id = fields.Char('Ref commit last')
        environnement_id = fields.Many2one('cloud.service.environnement')
        application_name = fields.Char('Nom de Application')
        
        @api.model
        def backup_dev(self):
            self.git_ref_id = 'jjjjjjj'
        
        def sauvegarder(self):
            return
        
        def deployer_vers_test(self):
            return
        
        def get_status_error_appli(self):
            return
        
        def get_view_commmit_log(self):
            return
            
        def add_domain_for_dev_environnement(self):
            return
        
        def get_domain(self):
            
            
            return
                
        def add_ssl_certification_for_dev_env(self):
            return
                


Cloud_Service_environnement_dev()

class Cloud_Service_environnement_live(models.Model):
        _name = 'cloud.service.environnement.live'
        
        environnement_id = fields.Many2one('cloud.service.environnement')
        service_param_host_git = fields.Text('parametre host pour git json')  
        service_param_host_db = fields.Text('parametre host db  json')  
        service_param_host = fields.Text('parametre host sftp json')  
        branche_id = fields.Char('Branche')
        tag_id = fields.Char('tag ')
        git_ref_id = fields.Char('Ref commit last')
        application_name = fields.Char('Nom de Application')
       
        def deployer_depuis_test(self):
            return
        
        def deployer_vers_test(self):
            return
       
Cloud_Service_environnement_live()




class Cloud_Service_environnement_branch(models.Model):
        _name = 'cloud.service.environnement.branch'
        
        name = fields.Char('Name')
        environnement_id = fields.Many2one('cloud.service.environnement')
        service_param_host_git = fields.Text('parametre host pour git json')  
        service_param_host_db = fields.Text('parametre host db  json')  
        service_param_host = fields.Text('parametre host sftp json')  
        branche_id = fields.Char('Branche')
        tag_id = fields.Char('tag ')
        git_ref_id = fields.Char('Ref commit last')
        application_name = fields.Char('Nom de Application')
       

        def branch_merge(self):
            raise Warning('Lorem ipsum dolor sit amet')
        
        
        def deployer_depuis_test(self):
            return
        
        def deployer_vers_test(self):
            return
       
Cloud_Service_environnement_branch()







class Cloud_Service_tmpl(models.Model):
        _name = 'cloud.service.tmpl'
   
        
        
        
        
        
        name = fields.Char('Nom du template Service Client', size=128)
        product_id = fields.Many2one('product.template', 'Produit lié')
        list_script_before = fields.Many2many('launch.script', string='Scripts de déploiement')
        
        
        
    
Cloud_Service_tmpl()



class cloud_service_config_param(models.Model):
        _name = 'cloud.service.config.param'
    
        name = fields.Char('nom')
       
    
cloud_service_config_param()


class cloud_service_fields(models.Model):
        _name = 'cloud.service.fields'
   
        name = fields.Char('champ')
        # type= fields.Selection('(list de champs possible)'),
        # html= fields.html('(mettre la valeur html)'),
        # valeur_du_champs= fields.Char('valeur du champs'),
    
cloud_service_fields()






class cloud_service_instance_service(models.Model):
        _name = 'cloud.service.instance.service'
   
        name = fields.Char('champ')
        # type= fields.Selection('(list de champs possible)'),
        # html= fields.html('(mettre la valeur html)'),
        # valeur_du_champs= fields.Char('valeur du champs'),
    
cloud_service_instance_service()


class cloud_service_host_param(models.Model):
        _name = 'cloud.service.host.param'
    
        name = fields.Char('nom du parametre')
        valeur = fields.Char('valeur du parametre')
        param_json_data = fields.Text('Data in json')
        host_ipv4 = fields.Char('Adress ipv4')
        host_ipv6 = fields.Char('Adress ipv6')
        hostname = fields.Char('Hostname')
        user_name = fields.Char('User name login ssh/sftp/ftp')
        host_path = fields.Char('path host')
        password = fields.Char('password user name')
        db_host = fields.Char('host db')
        db_name = fields.Char('nom de la base')
        db_password = fields.Char('db password')
        
       

        
        def copy_host_param_ansible_config(self):
            
            return file
            
        
        
cloud_service_host_param()













class cloud_service_api(models.AbstractModel):
    _name = 'cloud.service.api'
    
    
    
    
    def callcreateservice(self, type_service, url, requete_param_api, paramclient, obj_service_fournisseur):
        """ appel de l'api pour l'achat et la creation d'un service via le web service"""
          
        return True
    
    def call_get_order(type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_fournisseur):
        """ charger la commande en  pdf ou url""" 
        # on doit retourner les params ici retour_api_param_service nÃ©cÃ©ssaire pour le retour de l'api'
        # return un dict invoice = {order: name, file:{nname:name, data:data}, url:{url:url,name:name}  
       
        return True
    
    def call_get_invoice(type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_fournisseur):
        """ charger la facture en  pdf ou url""" 
        # on doit retourner les params ici retour_api_param_service nÃ©cÃ©ssaire pour le retour de l'api'
        # return un dict invoice = {invoice: name, file:{nname:name, data:data}, url:{url:url,name:name}  
        return True
    
    def call_check_statut_service(type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_fournisseur):
        """ apeler l'api pour connaitre le status du service crÃ©er"""
        return True
    
    
    
    
    def call_get_param_host(type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_fournisseur):
        """renvoie les parametre hosts (domain, ip, hostname, sql, login, password etc, du service crÃ©er """
        # renvoie les param_host 
        # c'est l'api spÃ©cifique qui s'occupe de la maniÃ¨re que doit Ãªtre recupÃ©rer les param hosts
        # host['host'] = {ip:xxxx, login:xxx, password,xxx, hostname, xxxx, db_host:xxx, db_name:xxxx, db_user:xxx, db_pass:xxxx}
        # host['stat'] = {statut:partiel ou complet} afin de relancer un cron pour 
        return True
    def call_add_param_host(self, type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_fournisseur):
        """renvoie les parametre hosts nouveau Ã  rajouter au services fournisseur pour configuerer un service client
         (domain, ip, hostname, sql, login, password etc, du service crÃ©er """
        return True
    
    
    def call_configure_service_and_add_param_host(self, type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_id, objet_service_fournisseur):
        
        return 
        
    
    
    def call_renew_service(self, type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_fournisseur):
      
        return True
    
    def call_get_date_expiration(self, type_service, url, requete_param_api, paramclient, retour_api_param_service, objet_service_fournisseur):
      
        return True
    
cloud_service_api()
# module dedauvia simple



# api requete gÃ©nÃ©rale / chaque api fournisseur devron surchargÃ© cette class
# afin de rajoutÃ© leur api 
class cloud_service_api_url_requete(models.Model):
        _name = 'cloud.service.api.url.requete'
   
   
   
        name = fields.Char('Name')
        fournisseur = fields.Many2one('res.partner', string='Fournisseur API', readonly=True)
        url = fields.Char('url', readonly=True)
        description = fields.Text('description')
        data_json = fields.Text('Parametre en Json', readonly=True)
        apibibindid = fields.Many2one('cloud.service.api.bibind', readonly=True)
        
        # param_ids = fields.One2many('cloud.service.requete.param','url_requete_id' , readonly=True)
        # fournisseur_name =fields.Char('nom fournisseur')
        # type= fields.Selection('(list de champs possible)'),
        # html= fields.html('(mettre la valeur html)'),
        # valeur_du_champs= fields.Char('valeur du champs'),
        
       
    
    
cloud_service_api_url_requete()

class cloud_service_fournisseur_api_requete_param(models.Model):
        _name = 'cloud.service.requete.param'
    
        name = fields.Char('nom')
        datatype = fields.Char('type de champ')
        paramtype = fields.Char('OÃ¹ le parametre (path, body)')
        is_requiered = fields.Boolean('est requis')
        is_enum = fields.Boolean('la valeur du champ est le champ selection', help='la valeur du champ est le champ selection enum_valeur et non le champ string valeur')
        description = fields.Char('description')
        is_client_param = fields.Char('Valeur donnÃ©e par le client')
        valeur = fields.Char('')
        enum_valeur = fields.Many2one('cloud.service.param.model', 'Choisr une valeur')
        tmpl_fournisseur_id = fields.Many2one('cloud.service.tmpl.fournisseur', 'requete url')
        url_id = fields.Many2one('cloud.service.api.url.requete', 'Url liÃ©')
        
                
            
    
cloud_service_fournisseur_api_requete_param()

class cloud_service_param_model(models.Model):
    _name = 'cloud.service.param.model'
    
    
    name = fields.Char('name')
    modeltype = fields.Char('Type de model')
    description = fields.Char('Description')


class cloud_service_fournisseur_param_client(models.Model):
        _name = 'cloud.service.paramclient'
    
        name = fields.Char('nom du parametre')
        valeur = fields.Char('valeur du parametre')
        param_json_data = fields.Text('Data in json')
    
cloud_service_fournisseur_param_client()




# module gandi


class cloud_service_fournisseur_api_requete_param(models.Model):
        _name = 'cloud.service.fournisseur.api.requete.param'
   
        name = fields.Char('nom', size=255)
        type = fields.Char('Type de champ', size=255)
        # model_call= fields.Many2one('TODO (si le champs peut Ãªtre appeler par un model)'),
        valeur = fields.Char('Valeur du param', size=128, help='valeur soit vide (rempli par le client, lors de la commande) soit prÃ©rempli (si lon veut determiner un service spÃ©cifique)')
        url_requet_id = fields.Many2one('cloud.service.api.url.requete', 'Id de url requete')
        
cloud_service_fournisseur_api_requete_param()

class cloud_service_categorie_fournisseur(models.Model):
        _name = 'cloud.service.categorie.fournisseur'
   
        name = fields.Char('nom', size=128)
        parent_id = fields.Many2one('cloud.service.categorie.fournisseur', string='Parent Category', select=True, ondelete='cascade')
        child_id = fields.One2many('cloud.service.categorie.fournisseur', 'parent_id', string='Child Categories')
        
        sequence = fields.Integer(string='Sequence', select=True)
    
cloud_service_categorie_fournisseur()


class cloud_service_categorie(models.Model):
        _name = 'cloud.service.categorie'
   
        name = fields.Char('nom', size=128)
        parent_id = fields.Many2one('cloud.service.categorie', string='Parent Category', select=True, ondelete='cascade')
        child_id = fields.One2many('cloud.service.categorie', 'parent_id', string='Child Categories')
        
        sequence = fields.Integer(string='Sequence', select=True)
    
cloud_service_categorie()

class cloud_service_category(models.Model):
        _name = 'cloud.service.category'
   
        name = fields.Char('nom', size=128)
        parent_id = fields.Many2one('cloud.service.category', string='Parent Category', select=True, ondelete='cascade')
        child_id = fields.One2many('cloud.service.category', 'parent_id', string='Child Categories')
        
        sequence = fields.Integer(string='Sequence', select=True)
    
cloud_service_category()

class cloud_service_fournisseur_category(models.Model):
        _name = 'cloud.service.fournisseur.category'
   
        name = fields.Char('nom', size=128)
        parent_id = fields.Many2one('cloud.service.fournisseur.category', string='Parent Category', select=True, ondelete='cascade')
        child_id = fields.One2many('cloud.service.fournisseur.category', 'parent_id', string='Child Categories')
        
        sequence = fields.Integer(string='Sequence', select=True)
    
cloud_service_fournisseur_category()


class cloud_service_type(models.Model):
        _name = 'cloud.service.type'
   
        name = fields.Char('nom', size=128)
        service_type = fields.Selection(selection=[('domaine', 'service domain'),
                                                  
                                                  ('hebergement', 'service hebergement'),
                                                  ('multi_hebergement', 'Multi hebergement sur hebergement'),
                                                  
                                                  ('serveur_dedie', 'service serveur dediÃ©'),
                                                  ('hebergement_sur_dedie', 'hebergement sur serveur dediÃ©'),
                                                  
                                                  ('machin_virtuelle', 'Machine virtuelle'),
                                                  ('hebergement_sur_vm', 'service hebergement sur vm'),
                                                  
                                                  ('service_pour_hÃ©bergement', 'services pour hÃ©bergement'),
                                                  ], select=True, ondelete='cascade')
        
        description = fields.Char(string='Type de service client')


cloud_service_type()


class cloud_service_renew_type(models.Model):
        _name = 'cloud.service.renew.type'
   
        name = fields.Char('nom', size=128)
        service_type = fields.Selection(selection=[('automatique', 'automatique'),
                                                  
                                                  ('manuel', 'manuel'),
                                                  ], select=True, ondelete='cascade')
        
        description = fields.Char(string='Type de service client')


cloud_service_type()



class cloud_service_fournisseur_type(models.Model):
        _name = 'cloud.service.fournisseur.type'
   
        name = fields.Char('nom', size=128)
        service_type = fields.Selection(selection=[('domaine', 'service domain'),
                                                  
                                                  ('hebergement', 'service hebergement'),
                                                  ('multi_hebergement', 'Multi hebergement sur hebergement'),
                                                  
                                                  ('serveur_dedie', 'service serveur dediÃ©'),
                                                  ('hebergement_sur_dedie', 'hebergement sur serveur dediÃ©'),
                                                  
                                                  ('machin_virtuelle', 'Machine virtuelle'),
                                                  ('hebergement_sur_vm', 'service hebergement sur vm'),
                                                  
                                                  ('service_pour_hÃ©bergement', 'services pour hÃ©bergement'),
                                                  ], select=True, ondelete='cascade')
         
        description = fields.Char(string='Type de service fournisseur')
        
        
        
    
cloud_service_fournisseur_type()


class product_category(models.Model):

    _inherit = 'product.category'

    
    provider_id = fields.Many2one('res.partner', string='Catégory de Provider')
       


   
         
         
               
