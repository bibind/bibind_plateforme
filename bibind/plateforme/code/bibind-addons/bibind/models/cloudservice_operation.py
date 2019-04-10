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
from openerp import SUPERUSER_ID

from openerp import models, fields, api, _
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

from socket import getaddrinfo

_logger = logging.getLogger("bibind_cloudservice")

class cloud_service_operation(models.Model):
    """operation"""
    _name = 'cloud.service.operation'
    _description = 'Operation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_begin'
    
    def selection_state(self):
        
        return [('draft','draft'),
                ('warning_po','La commande à plusieurs commande fournisseur et ce n\'est pas prévu'),
                ('en_attente_stock','Livraison fournisseur confirmer en attente'),
                
                ('service_fournisseur_partiellement_creer','Les services fournisseurs partiellement créer'),
                ('services_fournisseur_creer','Les services fournisseurs créer'),
                
                ('services_fournisseur_wait_achat','Les services fournisseurs en attente d\'achat'),
                ('services_fournisseur_partiel_acheter','Les services fournisseurs partiellement acheter'),
                ('services_fournisseur_acheter','Tous Les services fournisseurs acheter, en attente d\'activation'),
                
                ('service_fournisseur_partiel_done', 'services fournisseur partiellement  activer'),
                ('service_fournisseur_done', 'Tous les services fournisseur activer'),
                ('stock_done', 'Livraison fournisseur transferer et terminer'),
                
                ('services_client_creer', 'service client creer en brouillon'),
                ('services_client_traitement', 'services client en traitement'),
                ('services_client_partiel_traiement', 'service client creer en brouillon'),
                ('services_client_livrer','Tous les livraison services client transferer et terminer'),
                ('services_client_done','Tous services client terminer et activer')]
    
    
    
    state =fields.Selection(selection='selection_state')
    sale_order_id=fields.Many2one('sale.order', 'commande rerferante à l\'opération')
    purchase_order_id=fields.Many2one('purchase.order', 'Commande fournisseur référente')
    name=fields.Char('nom de l\'opération')
    livraison_fournisseur = fields.Many2one('stock.picking', 'Livraison service fournisseur')
    livraison_client = fields.Many2one('stock.picking', 'Livraison service client')
    so_has_multi_po = fields.Boolean('La commande à plusieurs commande fournisseur')
    cloud_service_operation_line_ids=fields.One2many('cloud.service.operation.line', 'cloud_service_operation_id', 'ligne de l\'operation')

     
     
    def create(self):
         
         return
     
     
     
    @api.multi 
    def check_and_confirm_purchase_order(self):
        """On confirme  la purchases commande pour être sur
        que tous les livraisons fournisseurs sont à jour depuis la creation de
        la sale order de l'operation.
        On verifie si la commande client est livrable, si la livraison est 
        en attente d'une opération"""
        
        sale_order = self.sale.order
        purchase_order =self.env['purchase.order'].browse([('pr_group_id','=',self.sale_order.name)])[0]
        
        
        if purchase_order.state=="draft":
            self.purchase_order_id = purchase_order.id
            purchase_order.wkf_confirm_order()
            
       
        return True

    def _get_stock_picking_of_sale_order_and_purchase_order(self):
        
        #on valide la po
        res_po = self.check_and_confirm_purchase_order()
        if res_po:
            #nbre de mouvement de la commande (avant de savoir si il y a une purchase order)
            picking = self.env['stock.picking']
            
            sale_order = self.sale_order_id
            
            sopick_ids = []
            
            sopick_ids = [picking.id for picking in sale_order.picking_ids]
            #verifier si il ya un approvisionnement en cour , purchase en cour
            picking_ids = picking.browse(cr, uid, sopick_ids, context)
            val =[]
            for picking in picking_ids:
                if picking.picking_type_code =='incoming':
                    self.livraison_fournisseur = picking.id
                    
                if picking.picking_type_code =='outcoming':
                    self.livraison_client == picking.id
                    if picking.state=='waiting':
                        val = {'state':'en_attente_stock'}
            self.write(val)
            self.create_services_fournisseur()
        else :
          return False 
      
      
    def _set_dependance_entre_operation_line(self):
        
        state_line = {}
        
        for opline in self.cloud_service_operation_line_ids:
            if opline.product_id.is_domain:
                param_requete_client = json.load(opline.sale_order_line_id.paramclient)
                if param_requete_client['domain_main']:
                    val = {'cloud_service_operation_id':opline}
                    op_line_domain_master = opline
                    state_line.append[opline]
        if len(state_line)>1:
            self.message_post([self.id], _('There is more at once domain main in operation sale %s') % (self.name))
            return False
        
        for op_line in self.cloud_service_operation_line_ids:
            if op_line.get_type_service_fournisseur()=='mutualise':
                res =op_line.write(val)
        if res:
            return True
        else :
            return False
        
        
                
        
         
            
         
        
    def create_services_fournisseur(self):
        """on créer les services fournisseurs sur odoo qui se chargerons de la demande du service
        via l'api du fournisseur """
        
        state_line = []
        for op_line in self.cloud_service_operation_line_ids:
            if not op_line.cloud_service_fournisseur_id:
                res = op_line.create_service_fournisseur()
                state_line.append(res)
        
        if all(item == True for item in state_line):
                self.state ="service_fournisseur_creer"
                self._set_dependance_entre_operation_line()
                
                self.call_api_services_fournisseur_paid()
            
        else:
            if any(item ==True for item in state_line):
                self.state ="service_fournisseur_partiellement_creer"
            else :
                self.state ="en_attente_stock"   
        
      
        
    def call_api_services_fournisseur_paid(self):
        """on lance la demande de service via les services fournisseur créer
        on verfie le résultat... ex : achat d'un nom de domain ovh ou gandi ..ovh ne retourne pas 
        de facture ..il faudra aller la chercher sur l'historique...Ou achat automatique d'un service plateforme Performance chez ovh
        hosting chez gandi qui retourne une facture ou une commande ...ici on ne récupere pas la commande ou la facture, lance juste la fonction de demande de création de service"""
        
        if self.state == 'services_fournisseur_creer':
            for op_line in self.cloud_service_operation_line_ids:
                
                res = op_line.call_fournisseur_service_commande_paid_pour_creation()
                
            if all(item == True for item in res):
                    self.state ="services_fournisseur_acheter"
                    self.check_services_fournisseur_is_paid()
            else:
                if any(item ==True for item in res):
                    self.state ="services_fournisseur_partiel_acheter"
                else :
                    self.state ="services_fournisseur_wait_achat"   
                
        else :
            res = self.create_services_fournisseur()
            return True
    
    def check_state_services_fournisseur_paid(self):
        """On verfie si les service à une facture ou commande payer
        on telecharge la facture ou commande et on la lie à la commande fournisseur
        si tous les services sont paye on met l'operation à paye et on met la commande fournisseur à paid
        on transfert les produits vers le stock pour les réserver au client
        """
        res =[]
        for op_line in self.cloud_service_operation_line_ids:
                res_state = op_line.is_fournisseur_paid()
                res.append(res_state)
    
        if all(item == True for item in res):
            self.state ="services_fournisseur_acheter"
            
        
        else:
            if any(item ==True for item in res):
                self.state ="services_fournisseur_partiel_acheter"
            else :
                self.state ="services_fournisseur_wait_achat"
    
    
    
    def transfert_purchase_picking(self):
        if self.state =="service_fournisseur_done":
           res = self.livraison_fournisseur.do_transfert()
           if self.purchase_order_id.state =="done":
               self.state="stock_done"
    
    
    def _services_fournisseurs_post_traitement(self):
        if self.state =="services_fournisseur_acheter":
            res =[]
            for op_line in self.cloud_service_operation_line_ids:
                op_line_res = op_line.client_service_post_traiment()
                res.append(op_line_res)
            
            if all(item == True for item in res):
                self.state ="service_fournisseur_done"
                self.transfert_purchase_picking()
                self._services_fournisseurs_create_service_client()
            
            else:
                if any(item ==True for item in res):
                    self.state ="service_fournisseur_partiel_done"
                else :
                    self.state ="services_fournisseur_acheter"
    
    def _services_fournisseurs_create_service_client(self):
        
         if self.state =="stock_done":
            res =[]
            for op_line in self.cloud_service_operation_line_ids:
                op_line_res = op_line.fournisseur_service_create_service_client()
                res.append(op_line_res)
            
            if all(item == True for item in res):
                self.state ="services_client_creer"
                self._services_fournisseurs_post_traitement()
                
            
            else:
                if any(item ==True for item in res):
                    self.state ="service_client_partiel_done"
                else :
                    self.state ="stock_done"
        
         return
     
    def _service_client_post_traitment(self):
        
        if self.state =="services_client_creer":
            res =[]
            for op_line in self.cloud_service_operation_line_ids:
                op_line_res = op_line.client_service_post_traitment()
                res.append(op_line_res)
            
            if all(item == True for item in res):
                self.state ="services_client_done"
                self.transfert_commande_picking()
                
            
            else:
                if any(item ==True for item in res):
                    self.state ="service_client_partiel_done"
                else :
                    self.state ="stock_done"
        
        return
    
    def _service_client_is_done(self):
        
        return
    
    def transfert_commande_picking(self):
        
        return
    
    
     
    
    
    
    
  
        
     
     
class cloud_service_operation_line(models.Model):
     """operation line"""
     _name = 'cloud.service.operation.line'
     _description = 'Operation line'
     _inherit = []
     _order = 'date_begin'
     
     
     def _selection_state(self):
        
        return [('draft','draft'),
                ('en_attente_stock','Livraison fournisseur en attente'),
                ('service_fournisseur_creer','le service fournisseur  créé')
                ('service_fournisseur_wait_achat','Le service fournisseur en attente d\'achat')
                ('service_fournisseur_acheter','Le service fournisseur acheter')
                ('stock_done', 'Livraison fournisseur terminer et service activer')
                ('service_client_cree', 'le service client creer')
                ('service_client_traitement', 'le service client en traitement')
                ('service_client_livrer','le service client livrer et activer')]

     
     state =fields.Selection(selection='_selection_state', string="Etat de l'operation")
     sale_order_id = fields.Many2one('sale.order', 'commande rerferante à l\'opération')
     product_id = fields.Many2one('product.template', 'product')
     sale_order_line_id=fields.Many2one('sale.order.line', 'ligne de commande')
     name=fields.Char('nom de l\'opération')
     procurement_in_id = fields.Many2one('procurement.order')
     procurement_out_id = fields.Many2one('procurement.order')
     move_lin_out =fields.Many2one('stock.move')
     move_lin_in = fields.Many2one('stock.move')
     
     
     cloud_service_operation_id=fields.Many2one('cloud.service.operation', 'Dépendance d\' une autre opération')
     
     cloud_service_fournisseur_id=fields.Many2one('cloud.service.fournisseur')
     service_fournisseur_is_paid = fields.Boolean('Le service fournisseur payé')
     cloud_service_id =fields.Many2one('cloud.service')
     
     
     
     
     def get_template_fournisseur_service(self):
           
            obj_service_tmpl_fournisseur = self.env['cloud.service.tmpl.fournisseur']
            fournisseur = product_id.seller_ids[0]
            prof_suplierinfo_id = pso.browse( fournisseur)
            template_service_fournisseur = obj_service_tmpl_fournisseur.browse(prof_suplierinfo_id.cloud_service_fournisseur_tmpl_id.id)
            
            return template_service_fournisseur
        
     def get_type_service_fournisseur(self):
         
         tmpl = self.get_template_fournisseur_service()
         
         return tmpl.type_service
        
     
     
     @api.multi
     def check_service_fournisseur(self):
         
         return self.cloud_service_fournisseur_id.check_state()
         
    
     
     @api.multi 
     def create_service_fournisseur(self):
         
         if not self.cloud_service_fournisseur_id:
             product = self.product_id
             obj_service_tmpl_fournisseur = self.pool.get('cloud.service.tmpl.fournisseur')
             obj_apif =self.pool.get('cloud.service.api.fournisseur')
             pso = self.pool.get('product.suplierInfo')
             obj_requete_api = self.pool.get('cloud.service.api.url.requete')
             service_fournisseur =self.pool.get('cloud.service.fournisseur')
             
             param_client = self.sale_order_line_id.param_client_id.id
             
             stf =[]
             fournisseur = product.seller_ids[0]
             prof_suplierinfo_id = pso.browse( fournisseur.id)
             template_service_fournisseur = obj_service_tmpl_fournisseur.browse(prof_suplierinfo_id.cloud_service_fournisseur_tmpl_id.id)
             lauch_scripts_ids = template_service_fournisseur.param_ids
             requete_api = obj_requete_api.browse(template_service_fournisseur.requete_api_service)
             apif = obj_apif.browse(template_service_fournisseur.api_fournisseur.id)
             api =apif.api_ref
             
             service_fournisseur_vals = {
                
                'state': 'draft', 
                'product_id':product,
                'service_fournisseur_tmpl_id': template_service_fournisseur,
                'fournisseur': fournisseur,
                'paramclient': param_client,
               
                }
             if self.product_id.is_domain_product :
                 param = json.load(self.sale_order_line_id.param_client_id)
                 service_fournisseur_vals.update({'is_domain':True,'domain':param['domain'], 'param_api_requete': param})
             elif self.get_type_service_fournisseur()=='mutualise' :
                 
                 domain_main = json.load(self.cloud_service_operation_id.sale_order_line_id.paramclient)['domain']
                 service_fournisseur_vals.update({'is_domain':False})
                 service_fournisseur_vals.update({'domain_main':domain_main, 'is_depend_domain': True})
      
         
             res = service_fournisseur.create(service_fournisseur_vals)
             
             #res.write({'launch_script_ids':(0, res.id,lauch_scripts_ids)})
              
             if res:
                self.write({'cloud_service_fournisseur_id':res, 'state':'service_fournisseur_creer'})
                rep = True
             else :
                self.write({'state':'en_attente_stock'})
                rep = False
             return rep
         else :
             return True
         
    
     @api.multi
     def call_fournisseur_service_commande_paid_pour_creation(self):
        if self.state =='service_fournisseur_creer':
             
             
             res = self.cloud_service_fournisseur_id.call_fournisseur_commande_service_create()
             if res :
                 self.service_fournisseur_is_paid = True
                 self.state ="service_fournisseur_acheter"
                 self.prepare_order_and_invoice()
             return res
         
        
        
    
     @api.multi
     def prepare_order_and_invoice(self):
            if self.service_fournisseur_is_paid:
                data_order = self.cloud_service_fournisseur_id.call_get_order()
                if data_order:
                    attachment = self.env['ir.attachment']
                    for data in data_order:
                        if data['order']['url']:
                            document_vals = {'name': data['order']['name'],
                                            'url': data['order']['url'],
                                            'res_model': 'purchase.order',
                                            'res_id': self.cloud_service_operation_id.purchase_order_id.id,
                                            'type': 'url' }
                            attachment.create(document_vals)
                            
                        if data['order']['file']:
                            document_vals = {'name': data['order']['file']['name'],
                                            'datas': data['order']['file']['data'],
                                            'res_model': 'purchase.order',
                                            'datas_fname': data['order']['file']['name'],
                                            'res_id': self.cloud_service_operation_id.purchase_order_id.id,
                                            'type': 'binary' }
                            attachment.create(document_vals)
                        if data['invoice']['url']:
                            document_vals = {'name': data['invoice']['name'],
                                            'url': data['invoice']['url'],
                                            'res_model': 'purchase.order',
                                            'res_id': self.cloud_service_operation_id.purchase_order_id.id,
                                            'type': 'url' }
                            attachment.create(document_vals)
                            
                        if data['invoice']['file']:
                            document_vals = {'name': data['invoice']['file']['name'],
                                            'datas': data['invoice']['file']['data'],
                                            'res_model': 'purchase.order',
                                            'datas_fname': data['invoice']['file']['name'],
                                            'res_id': self.cloud_service_operation_id.purchase_order_id.id,
                                            'type': 'binary' }
                            attachment.create(document_vals)
            
                    return 
    
     @api.multi    
     def is_fournisseur_paid(self):
         
         return True
     
     
     
     @api.multi
     def call_activation_fournisseur_service(self):
        
        return
    
    
    
     @api.multi
     def fournisseur_service_post_traitement(self):
        
        return
    
    
     @api.multi
     def fournisseur_is_done(self):
         
         return
     
     
     
     
     @api.multi
     def fournisseur_service_create_service_client(self):
        
         if not self.cloudservice:
             product = self.product_id
             obj_service_tmpl = self.pool.get('cloud.service.tmpl')
          
             obj_service_tmpl_fournisseur = self.pool.get('cloud.service.tmpl.fournisseur')
             obj_apif =self.pool.get('cloud.service.api.fournisseur')
             pso = self.pool.get('product.suplierInfo')
             obj_requete_api = self.pool.get('cloud.service.api.url.requete')
             service_fournisseur =self.cloud_service_fournisseur_id
             service = self.env['cloud.service']
             param_client = self.sale_order_line_id.param_client_id.id
             
             stf =[]
             fournisseur = product.seller_ids
             prof_suplierinfo_id = pso.browse( prof_suplierinfo.id)
             template_service_fournisseur = obj_service_tmpl_fournisseur.browse(prof_suplierinfo_id.cloud_service_fournisseur_tmpl_id.id)
             
             requete_api = obj_requete_api.browse(template_service_fournisseur.requete_api_service)
             apif = obj_apif.browse(template_service_fournisseur.api_fournisseur.id)
             api =apif.api_ref
             
             service_vals = {
                
                'state': 'draft', 
                'product_id':self.product_id,
                'partner_id':self.sale_order_id.partner_id,
                'cloud_service_tmpl_id': self.product_id.cloud_service_tmpl_id.id,
                'cloud_service_fournisseur_id': self.cloud_service_fournisseur_id,
                'founisseur': fournisseur,
                'instance_service': self.product_id.cloud_service_tmpl_id.instance_de_gestion.id,
                
                  
                }
                 
   
       
      
             
             
             if self.product_id.is_domain_product :
                 param = self.sale_order_line_id.param_client_id.param
                 service_vals.update({'is_domain':True,'domain':param['domain'], 'param_api_requete': param})
             else :
                 service_vals.update({'is_domain':False})
         
             res = service.create(service_vals)
             if res:
                self.write({'cloud_service_id':res, 'state':'service_creer'})
                rep = True
             else :
                self.write({'state':'en_attente_stock'})
                rep = False
             return rep
         else :
             return True
        
    
     @api.multi
     def client_service_is_(self):
        
        return
    
     @api.multi
     def client_service_active(self):
        
        return
    
    
     @api.multi
     def client_service_is_active(self):
        
        return
    
    
     @api.multi
     def client_service_post_traitment(self):
        if self.state=="service_fournisseur_acheter":
            ser_four = self.cloud_service_fournisseur_id.post_traitement()
        
            
        
        return
    
     
     @api.multi
     def client_service_is_done(self):
        
        return