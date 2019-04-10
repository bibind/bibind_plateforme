# -*- coding: utf-8 -*-
import cStringIO
import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET

import logging
import re

import werkzeug.utils
import urllib2
import werkzeug.wrappers
from PIL import Image

import openerp
from openerp.addons.web.controllers.main import WebClient
from openerp.addons.web import http
from openerp.http import  Controller , request, route, STATIC_CACHE
from openerp.tools import image_save_for_web
from ..tools import make_response, eval_request_params

_logger = logging.getLogger("bibind_cloudservice")



    


class Console(openerp.addons.web.controllers.main.Home):
    #------------------------------------------------------
    # View
    #------------------------------------------------------
    @http.route('/console', type='http', auth="user",)
    def console(self, s_action=None, **kw):
        
        _logger.info('******request : %s' % (request.uid))
        groupuser = request.env['res.users'].browse(request.uid).has_group('base.group_user')
        groupbibinduser = request.env['res.users'].browse(request.uid).has_group('bibind.group_user')
        #_logger.info('******request societe : %s' % (societe))
        #_logger.info('******request name : %s' % (name))
        if not groupuser and groupbibinduser:
            if request.session.uid:
                if kw.get('redirect'):
                    return werkzeug.utils.redirect(kw.get('redirect'), 303)
                if not request.uid:
                    request.uid = request.session.uid
    
                menu_data = request.registry['ir.ui.menu'].load_menus(request.cr, request.uid, context=request.context)
                return request.render('bibind.bibindwebclient_bootstrap', qcontext={'menu_data': menu_data})
            else:
                return login_redirect()
        else :
            if request.session.uid:
                if kw.get('redirect'):
                    return werkzeug.utils.redirect(kw.get('redirect'), 303)
                if not request.uid:
                    request.uid = request.session.uid
    
                menu_data = request.registry['ir.ui.menu'].load_menus(request.cr, request.uid, context=request.context)
                return request.render('web.webclient_bootstrap', qcontext={'menu_data': menu_data})
            else:
                return login_redirect()


        


class RestApi(Controller):
    """
    /api/auth                   POST    - Login in Odoo and set cookies

    /api/<model>                GET     - Read all (with optional domain, fields, offset, limit, order)
    /api/<model>/<id>           GET     - Read one (with optional fields)
    /api/<model>                POST    - Create one
    /api/<model>/<id>           PUT     - Update one
    /api/<model>/<id>           DELETE  - Delete one
    /api/<model>/<id>/<method>  PUT     - Call method (with optional parameters)
    """

    def session_info(self, request):
        request.session.ensure_valid()
        return {
            "session_id": request.session_id,
            "uid": request.session.uid,
            "user_context": request.session.get_context() if request.session.uid else {},
            "db": request.session.db,
            "username": request.session.login,
            "company_id": request.env.user.company_id.id if request.session.uid else None,
        }

    @route('/api/echo', auth='none', methods=["GET"])
    @make_response()
    def describr(self,):
        # Before calling /api/auth, call /web?db=*** otherwise web service is not found
        return {'hello_word':'hello word'}


    @route('/api/auth', auth='none', methods=["POST"])
    @make_response()
    def authenticate(self, db, login, password):
        # Before calling /api/auth, call /web?db=*** otherwise web service is not found
        request.session.authenticate(db, login, password)
        return self.session_info(request)

    @route('/api/<string:model>', auth='user', methods=["GET"])
    @make_response()
    def search_read(self, model, **kwargs):
        eval_request_params(kwargs)
        return request.env[model].search_read(**kwargs)

    @route('/api/<string:model>/<int:id>', auth='user', methods=["GET"])
    @make_response()
    def read(self, model, id, **kwargs):
        eval_request_params(kwargs)
        result = request.env[model].browse(id).read(**kwargs)
        return result and result[0] or {}

    @route('/api/<string:model>', auth='user',
           methods=["POST"], csrf=False)
    @make_response()
    def create(self, model, **kwargs):
        eval_request_params(kwargs)
        return request.env[model].create(**kwargs).id

    @route('/api/<string:model>/<int:id>', auth='user',
           methods=["PUT"], csrf=False)
    @make_response()
    def write(self, model, id, **kwargs):
        eval_request_params(kwargs)
        return request.env[model].browse(id).write(**kwargs)

    @route('/api/<string:model>/<int:id>', auth='user',
           methods=["DELETE"], csrf=False)
    @make_response()
    def unlink(self, model, id):
        return request.env[model].browse(id).unlink()

    @route('/api/<string:model>/<int:id>/<string:method>', auth='user',
           methods=["PUT"], csrf=False)
    @make_response()
    def custom_method(self, model, id, method, **kwargs):
        eval_request_params(kwargs)
        record = request.env[model].browse(id)
        return getattr(record, method)(**kwargs)
