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

from openerp.exceptions import Warning
from openerp import models, fields, api, _
from openerp import pooler, tools
from openerp.tools.translate import _
from openerp.osv.expression import get_unaccent_wrapper
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
from pygments.lexer import _inherit

import gitlab

_logger = logging.getLogger("bibind_cloudservice")



class bibind_api_gitlab(models.Model):
    _name = 'bibind.api.gitlab'
    description = 'gestion des depots avec gitlab'
    
    host_gitlab = fields.Char('Url du gitlab' , default='https://lab.bibind.com/')
    token_admin_generique = fields.Char('Token Admin' , default='3Kb2LjfCW-Qn1RLyTP2y')
    
    def _get_api_static(self):
        
        gl = gitlab.Gitlab('https://lab.bibind.com/', '3Kb2LjfCW-Qn1RLyTP2y', ssl_verify=False)
        gl.auth()
        return gl
    
    def create_user(self, user, vals):
       
             gl = self._get_api_static()
             username = vals['name'].replace(" ", "")
             user_data = {'email': vals['email'],  'username': username, 'name': vals['name'],  'password': vals['password'],}
             try:
                 gitlab_user = gl.users.create(user_data)
                 return gitlab_user
             except gitlab.exceptions.GitlabAuthenticationError:
                 return False
             
    def create_project(self, username, projectname, import_url):
             _logger.info('+depot gitlab %s  ' %(username) ) 
             _logger.info('+depot gitlab %s  ' %(projectname) ) 
             gl = self._get_api_static()
             
             try: 
                projet = gl.projects.create({'name': projectname, 'import_url': import_url}, sudo=username)
                return projet
             except gitlab.exceptions.GitlabAuthenticationError:
                 return False
            
             
            
        
        


class bibind_depot(models.Model):
    
    _name = 'bibind.depot'


    name = fields.Char('Nom du dépot')
    gitlab_projet_id= fields.Char('Gitlab projet id')
    bibind_user_id = fields.Many2one('bibind.user', 'createur du dépot')
    partner_id = fields.Many2one('res.partner', related="bibind_user_id.partner_id")
    url = fields.Char('url du depot', related='ssh_url')
    ssh_url = fields.Char('ssh url du depot')
    http_url = fields.Char('https url du depot')
    projet_name = fields.Char('Gitlab projet name')
    runner_token = fields.Char('Gitlab runner token')
    gitlab_web_url= fields.Char('Gitlab web url')
    
    depot_state= fields.Boolean('depot is empty')
    
    def bibind_create_depot(self, bibind_user, depotname, import_url):
        
         _logger.info('+depot depot %s  ' %(bibind_user) )
         _logger.info('+depot depot %s  ' %(depotname) )
         gitlab = self.env['bibind.api.gitlab']
        
         p = gitlab.create_project(bibind_user.gitlab_username, depotname, import_url)  
         _logger.info('+gitlab %s  ' %( p) )
         projet_vals = {}
         projet_vals = {
                'name':p.name,
                'gitlab_projet_id': p.id,
                'bibind_user_id':bibind_user.id, 
                'ssh_url' : p.ssh_url_to_repo,
                'http_url' : p.http_url_to_repo,
                'projet_name' : p.name,
                'runner_token' : p.runners_token,
                'gitlab_web_url' : p.web_url
                }
            
            
         depotid = self.create(projet_vals)
         return depotid
     
    def populate_depot(self, service, **kwargs):
         
        DIRECTORY=self.bibind_user_id.home
        GIT_PROJET=self.ssh_url
        APP_URL=service.application.url
        APP_NAME=service.application.folder
        PROJET_DIRECTORY=self.projet_name
     
        cmd ='sh /mnt/extra-addons/bibind/models/depots/scripts/populate_depot.sh '+DIRECTORY+' '+GIT_PROJET+' '+APP_URL+' '+APP_NAME+' '+PROJET_DIRECTORY
          
        proc = subprocess.Popen([ cmd ],shell=True, close_fds=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        
        if proc.returncode==1 and err==None:
            self.write({'depot_state':True})
            return True
        else:
            return False
        
    
   
bibind_depot()