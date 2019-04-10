# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import logging
import time
from openerp import models, fields, api


_logger = logging.getLogger("bibind_cloudservice")




class wizard_destroy_confirm(models.TransientModel):
    """requete configuration"""
    _name = "wizard.destroy.confirm"
    
    
    @api.multi
    def action_confirm(self):
       
       node = self.env['cloud.service.node'].browse(self._context['node_id'])
       node.destroy_node()
       return {
            'type': 'ir.actions.act_window',
            'res_model': 'cloud.service.node',
            'res_id': node.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'nodestroy': True,
        }
       
       
wizard_destroy_confirm()


class wizard_import_rancher(models.TransientModel):
    """requete configuration"""
    _name = "wizard.import.rancher"
    
    
    @api.multi
    def action_confirm(self):
       
        api = self.env.ref('bibind.bibind_api_container_rancher')
        env = api.get_rancher_environnement(self)
        project_rancher = self.env['bibind.rancher.project']
        
        for e in env:
            vals = {}
            vals= {
                'name':e['name'],
                'project_name':e['name'],
                'project_id':e['id'],
                }
            project_rancher.create(vals)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'bibind.rancher.project',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }
       
       
wizard_import_rancher()

class services_builder_image(models.TransientModel):
    """requete configuration"""
    _name = 'services.builder.image'
    
    
    def _get_list_images(self):
        images = []
        if self._context.get('fournisseur_api'):
            fournisseur_api = self.env['service.cloud.api.fournisseur'].browse(self._context.get('fournisseur_api'))
           
            list = fournisseur_api.list_images()
        for key in list:
            images.append((key, key))
        return list
    
    def _get_default_fournisseur(self):
        if self._context.get('fournisseur_id'):
            
            return  self._context.get('fournisseur_id')
        
        
        
        
    fournisseur = fields.Many2one('res.partner', default='_get_default_fournisseur')
    images=fields.Selection(selection='_get_list_images', string='Choisir une image')
    
    




class services_builder(models.TransientModel):
    """requete configuration"""
    _name = 'services.builder'

    
    
    def _default_provider(self):
        return self._context.get('name')
    
    def _default_service(self):
        if self._context.get('service_id'):
            return self.env['cloud.service'].search([('id','=',self._context.get('service_id'))]).id
        else:
            return False
        
        
    def _default_confirm(self):
        if self._context.get('is_confirm'):
            return True
        else:
            return False
        
    def _default_propress(self):
        _logger.info('defaut progress bar  : %s' % (self._context.get('progressbarok')))
      
        if self._context.get('progressbarok'):
            return 26
        else:
            return 0
        
    

    def _default_products(self):
        result = {}
        category = self.env['product.category'].search([('provider_id','=',self._context.get('provider_id'))])
        return self.env['product.template'].search([('categ_id','=',category.id)]).ids
        
        
    
    name = fields.Char(string='name', size=128)
    
    name_projet = fields.Char(string='Nom du projet', size=128)
    
    nameprojetdnsdev = fields.Char(string='Url environnement dev', size=128)
    
    nameprojetdnstest = fields.Char(string='Url environnement test', size=128)
    
    nameprojetdnslive = fields.Char(string='Url environnement live', size=128)
    
    
    partner_id=fields.Many2one('res.partner', string='Client', required=True, default=lambda self: self.env.user.partner_id)
    
    
    service_id=fields.Many2one('cloud.service', default=_default_service)
    
    provider_id=fields.Many2one('res.partner', string='Provider')
    
    category_id=fields.Char(string='Catégory')
    
    product_id=fields.Many2one('product.template',string='Les offres')


    category_application_id=fields.Many2one('bibind.application.category',string='Type d\'application')
    
    category_app_id=fields.Char(string='app Catégory')
    
    application_ids=fields.Many2one('bibind.application', string='Application')
    
    
    state=fields.Selection([('name_projet','Nom de votre projet'),('Provider','Choisir son provider'), ('offres_environnement','Choisire une offre Environnement'),('application','Choisir son application'),('run',' lancer son projet'), ('progress',' Service en creation')], default='name_projet')
      
    progressbar = fields.Float(string="Progression", default=_default_propress)
    run_button = fields.Char('bouton run ')
    is_confirm = fields.Boolean(default=False)
    
    
    @api.onchange('run_button')
    def progress_change(self):
        _logger.info('befor button  : %s' % (self.progressbar))
      

    @api.onchange('progressbar')
    def onchange_progressbar(self):
        
        _logger.info('on change progress  : %s' % (self.progressbar))

    @api.onchange('name_projet')
    def onchange_projet_name(self):
        
        res = {}
        _logger.info('project name  : %s' % (self.name_projet))
        if not self.name_projet :
            return False
        else:
            rec = self.env['cloud.service'].projetname_search(self.name_projet)
            
            if  rec:
                res = { 'warning': {'title': 'Le nom exist déja', 'message':'Veuillez en choisir un autre'} }
                return res
            else:
                self.nameprojetdnsdev ="dev-"+self.name_projet+".bibind.com"
                self.nameprojetdnstest ="test-"+self.name_projet+".bibind.com"
                self.nameprojetdnslive ="live-"+self.name_projet+".bibind.com"
          
    @api.onchange('provider_id')
    def onchange_provider_id(self):
        if not self.provider_id :
            return False
        else :
            category = self.env['product.category'].search([('provider_id','=',self.provider_id.id)])
            self.category_id = category.ids
            self.state = 'offres_environnement'
            return {'domain':{'product_id': [('categ_id', 'in', category.ids)]}}
          
      
    @api.onchange('category_application_id')
    def onchange_category_application(self):
        categoryapp = self.env['bibind.application.category'].search([('id','=',self.category_application_id.id)])
        self.category_app_id = categoryapp.ids
        return {'domain':{'application_ids': [('category', 'in',categoryapp.ids )]}}
      
      
      
    def get_next_step(self, step):
        
        if step=='name_projet':
            return 'Provider'
        if step=='Provider':
            return 'offres_environnement'
        if step=='offres_environnement':
            return 'application'
        if step=='application':
            return 'run'
        if step=='run':
            return 'progress'
        if step=='progress':
            return 'progress'
        
    def get_previous_step(self, step):
        
        if step=='name_projet':
            return 'name_projet'
        if step=='Provider':
            return 'name_projet'
        if step=='offres_environnement':
            return 'Provider'
        if step=='application':
            return 'offres_environnement'
        if step=='run':
            return 'application'
        if step=='progress':
            return 'run'
    
    @api.multi
    def action_next(self):
      #your treatment to click  button next 
      #...
      provider =self.provider_id
    
      
      step =self.state
     
      next_step = self.get_next_step(step)
      # update state to  step2
      self.write( {'state': next_step})
     
      #return view
      return {
            'name':'Wordpress continous',
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'res_model': 'services.builder',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'res_id': self.id,
          
            'target': 'current',
            
            
             }
      
      
    @api.multi  
    def action_previous(self):
      #your treatment to click  button next 
      #...
      # update state to  step2
      step =self.state
      previous_step = self.get_previous_step(step)
      # update state to  step2
      self.write( {'state': previous_step})
     
      #return view
      return {
            'name':'Wordpress continous',
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'res_model': 'services.builder',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'res_id': self.id,
          
            'target': 'current',
            
            
             }
      
      
    def get_service_fournisseur_available(self):
        
        return  
      
    
    
    
    
    @api.multi
    def confirm(self):
          
      provider =self.provider_id
      step =self.state
      self.is_confirm =True
      self = self.with_context(progressbarok=True)
      next_step = self.get_next_step(step)
      # update state to  step2
      self.write( {'state': next_step})
      _logger.info('context  : %s' % (self.env.context))
      #return view
      return {
            'name':'Service en création',
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'res_model': 'services.builder',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'res_id': self.id,
          
            'target': 'new',
            
            
             }
      
      
      
      
      
    @api.multi
    def action_server_maybe(self):
        rec = self.env['cloud.service'].projetname_search(self.name_projet)
        if  rec:
            res = { 'warning': {'title': 'Le nom exist déja', 'message':'Veuillez en choisir un autre'} }
            return res
            self.write( {'state': 'name_projet'})
             
              #return view
            return {
                    'name':'Créer un service',
                    'context': self.env.context,
                    'type': 'ir.actions.act_window',
                    'res_model': 'services.builder',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [(False, 'form')],
                    'res_id': self.id,
                    'target': 'new',
                     }
        
       
        service_fournisseur_exist = self.env['cloud.service.fournisseur'].browse([('product_id','=',self.product_id),('availaible_service','>',0)])
        countsf =len(service_fournisseur_exist)
        if service_fournisseur_exist and countsf==1:
            sf = service_fournisseur_exist[0]
            sf.prepare_service()
            service_client = sf.create_service_client()
        else:
            service_fournisseur =self.env['cloud.service.fournisseur']
            product = self.env['product.template'].browse(self.product_id.id)
            fournisseur_template = elf.env['cloud.service.tmpl.fournisseur'].browse(self.product_id.cloud_service_fournisseur_tmpl_id.id)
            vals_fournisseur ={
                'fournisseur':self.provider_id,
                'product_id':product.id,
                'type_service': fournisseur_template.type_service,
                'nbr_service':fournisseur_template.nbr_service_client,
                
                }
            sf_id = service_fournisseur.create(vals_fournisseur)
            sf.prepare_service()
            
            service_client = sf.create_service_client()
        
            service =self.pool.get('cloud.service')
            
        return {'type': 'ir.actions.act_window_close'}

services_builder()





class wizard_wordpress_continous(models.TransientModel):
    """requete configuration"""
    _name = 'wizard.wordpress.continous'

    
    
    def _default_provider(self):
        return self._context.get('name')
    
    def _default_service(self):
        if self._context.get('service_id'):
            return self.env['cloud.service'].search([('id','=',self._context.get('service_id'))]).id
        else:
            return False
        
        
    def _default_confirm(self):
        if self._context.get('is_confirm'):
            return True
        else:
            return False
        
    def _default_propress(self):
        _logger.info('defaut progress bar  : %s' % (self._context.get('progressbarok')))
      
        if self._context.get('progressbarok'):
            return 26
        else:
            return 0
        
    

    def _default_products(self):
        result = {}
        category = self.env['product.category'].search([('provider_id','=',self._context.get('provider_id'))])
        return self.env['product.template'].search([('categ_id','=',category.id)]).ids
        
        
    
    name = fields.Char(string='name', size=128)
    
    name_projet = fields.Char(string='Nom de votre site', size=128,  required=True)
    
    nameprojetdnsdev = fields.Char(string='Url environnement dev', size=128)
    
    nameprojetdnstest = fields.Char(string='Url environnement test', size=128)
    
    nameprojetdnslive = fields.Char(string='Url environnement live', size=128)
    
    
    partner_id=fields.Many2one('res.partner', string='Client', required=True, default=lambda self: self.env.user.partner_id)
    
    
    service_id=fields.Many2one('cloud.service', default=_default_service)
    
    provider_id=fields.Many2one('res.partner', string='Provider')
    
    category_id=fields.Char(string='Catégory')
    
    product_id=fields.Many2one('product.template',string='Les offres')


    category_application_id=fields.Many2one('bibind.application.category',string='Type d\'application')
    
    category_app_id=fields.Char(string='app Catégory')
    
    application_ids=fields.Many2one('bibind.application', string='Application')
    
    
    state=fields.Selection([('name_projet','Nom de votre projet'),('Provider','Choisir son provider'), ('offres_environnement','Choisire une offre Environnement'),('application','Choisir son application'),('run',' lancer son projet'), ('progress',' Service en creation')], default='name_projet')
      
    progressbar = fields.Float(string="Progression", default=_default_propress)
    run_button = fields.Char('bouton run ')
    is_confirm = fields.Boolean(default=False)
    
    
    @api.onchange('run_button')
    def progress_change(self):
        _logger.info('befor button  : %s' % (self.progressbar))
      

    @api.onchange('progressbar')
    def onchange_progressbar(self):
        
        _logger.info('on change progress  : %s' % (self.progressbar))

    @api.onchange('name_projet')
    def onchange_projet_name(self):
        
        res = {}
        _logger.info('project name  : %s' % (self.name_projet))
        if not self.name_projet :
            return False
        else:
            rec = self.env['cloud.service'].projetname_search(self.name_projet)
            
            if  rec:
                res = { 'warning': {'title': 'Le nom exist déja', 'message':'Veuillez en choisir un autre'} }
                return res
            else:
                self.nameprojetdnsdev ="dev-"+self.name_projet+".bibind.com"
                self.nameprojetdnstest ="test-"+self.name_projet+".bibind.com"
                self.nameprojetdnslive ="live-"+self.name_projet+".bibind.com"
          
    @api.onchange('provider_id')
    def onchange_provider_id(self):
        if not self.provider_id :
            return False
        else :
            category = self.env['product.category'].search([('provider_id','=',self.provider_id.id)])
            self.category_id = category.ids
            self.state = 'offres_environnement'
            return {'domain':{'product_id': [('categ_id', 'in', category.ids)]}}
          
      
    @api.onchange('category_application_id')
    def onchange_category_application(self):
        categoryapp = self.env['bibind.application.category'].search([('id','=',self.category_application_id.id)])
        self.category_app_id = categoryapp.ids
        return {'domain':{'application_ids': [('category', 'in',categoryapp.ids )]}}

    def get_next_step(self, step):
        
        if step=='name_projet':
            return 'Provider'
        if step=='Provider':
            return 'offres_environnement'
        if step=='offres_environnement':
            return 'application'
        if step=='application':
            return 'run'
        if step=='run':
            return 'progress'
        if step=='progress':
            return 'progress'
        
    def get_previous_step(self, step):
        
        if step=='name_projet':
            return 'name_projet'
        if step=='Provider':
            return 'name_projet'
        if step=='offres_environnement':
            return 'Provider'
        if step=='application':
            return 'offres_environnement'
        if step=='run':
            return 'application'
        if step=='progress':
            return 'run'
    
    @api.multi
    def action_next(self):
      #your treatment to click  button next 
      #...
      provider =self.provider_id
    
      
      step =self.state
     
      next_step = self.get_next_step(step)
      # update state to  step2
      self.write( {'state': next_step})
     
      #return view
      return {
            'name':'Wordpress continous',
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'res_model': 'services.builder',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'res_id': self.id,
          
            'target': 'current',
            
            
             }
      
      
    @api.multi  
    def action_previous(self):
      #your treatment to click  button next 
      #...
      # update state to  step2
      step =self.state
      previous_step = self.get_previous_step(step)
      # update state to  step2
      self.write( {'state': previous_step})
     
      #return view
      return {
            'name':'Wordpress continous',
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'res_model': 'services.builder',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'res_id': self.id,
          
            'target': 'current',
            
            
             }
      
      
    def get_service_fournisseur_available(self):
        
        return  
      
    
    
    
    
    @api.multi
    def confirm(self):
          
      provider =self.provider_id
      step =self.state
      self.is_confirm =True
      self = self.with_context(progressbarok=True)
      next_step = self.get_next_step(step)
      # update state to  step2
      self.write( {'state': next_step})
      _logger.info('context  : %s' % (self.env.context))
      #return view
      return {
            'name':'Service en création',
            'context': self.env.context,
            'type': 'ir.actions.act_window',
            'res_model': 'services.builder',
            'view_mode': 'form',
            'view_type': 'form',
            'views': [(False, 'form')],
            'res_id': self.id,
          
            'target': 'new',
            
            
             }
      
      
      
      
      
    @api.multi
    def action_server_maybe(self):
        rec = self.env['cloud.service'].projetname_search(self.name_projet)
        if  rec:
            res = { 'warning': {'title': 'Le nom exist déja', 'message':'Veuillez en choisir un autre'} }
            return res
            self.write( {'state': 'name_projet'})
             
              #return view
            return {
                    'name':'Créer un service',
                    'context': self.env.context,
                    'type': 'ir.actions.act_window',
                    'res_model': 'services.builder',
                    'view_mode': 'form',
                    'view_type': 'form',
                    'views': [(False, 'form')],
                    'res_id': self.id,
                    'target': 'new',
                     }
        
       
        service_fournisseur_exist = self.env['cloud.service.fournisseur'].browse([('product_id','=',self.product_id),('availaible_service','>',0)])
        countsf =len(service_fournisseur_exist)
        if service_fournisseur_exist and countsf==1:
            sf = service_fournisseur_exist[0]
            sf.prepare_service()
            service_client = sf.create_service_client()
        else:
            service_fournisseur =self.env['cloud.service.fournisseur']
            product = self.env['product.template'].browse(self.product_id.id)
            fournisseur_template = elf.env['cloud.service.tmpl.fournisseur'].browse(self.product_id.cloud_service_fournisseur_tmpl_id.id)
            vals_fournisseur ={
                'fournisseur':self.provider_id,
                'product_id':product.id,
                'type_service': fournisseur_template.type_service,
                'nbr_service':fournisseur_template.nbr_service_client,
                
                }
            sf_id = service_fournisseur.create(vals_fournisseur)
            sf.prepare_service()
            
            service_client = sf.create_service_client()
        
            service =self.pool.get('cloud.service')
            
        return {'type': 'ir.actions.act_window_close'}

wizard_wordpress_continous()



class wizard_ansible_execute(models.TransientModel):
    """requete configuration"""
    _name = "wizard.ansible.execute"
    
    def _default_context(self):
        _logger.info('context  : %s' % (self._context))
      
        if self._context.get('active_ids'):
            return self._context.get('active_ids')
        else:
            return 0
        
    name = fields.Char(string='name', size=128)
    log = fields.Char(string='log', size=128, default=_default_context)
    scripts = fields.Many2many('launch.script')
    
    @api.multi
    def action_confirm(self):
       result ={}
       for script in self.scripts:
           res = script.run_script(self.log)
           result.update(res)
       return True
       
       
wizard_ansible_execute()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
