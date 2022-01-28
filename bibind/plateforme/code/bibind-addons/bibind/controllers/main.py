# -*- coding: utf-8 -*-

import base64
import copy
import datetime
import functools
import hashlib
import io
import itertools
import json
import logging
import operator
import os
import re
import sys
import tempfile
import unicodedata
from collections import OrderedDict, defaultdict

import babel.messages.pofile
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from lxml import etree, html
from markupsafe import Markup
from werkzeug.urls import url_encode, url_decode, iri_to_uri

import odoo
import odoo.modules.registry
from odoo.api import call_kw

from odoo.modules import get_resource_path, module
from odoo.tools import html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr, osutil
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open, file_path
from odoo.tools.safe_eval import safe_eval, time
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security

from odoo.addons.web.controllers.main import WebClient


from ..tools import make_response, eval_request_params

_logger = logging.getLogger("bibind_cloudservice")



    


class Console(odoo.addons.web.controllers.main.Home):
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
                    context = request.env['ir.http'].webclient_rendering_context()
                    response = request.render('bibind.bibindwebclient_bootstrap', qcontext=context)
                    response.headers['X-Frame-Options'] = 'DENY'
                    return response
            else:
                return login_redirect()
        else :
            if request.session.uid:
                if kw.get('redirect'):
                    return werkzeug.utils.redirect(kw.get('redirect'), 303)
                if not request.uid:
                    request.uid = request.session.uid
    
                context = request.env['ir.http'].webclient_rendering_context()
                response = request.render('bibind.bibindwebclient_bootstrap', qcontext=context)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
            else:
                return login_redirect()


        


class RestApi(http.Controller):
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

    @http.route('/api/echo', auth='none', methods=["GET"])
    @make_response()
    def describr(self,):
        # Before calling /api/auth, call /web?db=*** otherwise web service is not found
        return {'hello_word':'hello word'}


    @http.route('/api/auth', auth='none', methods=["POST"])
    @make_response()
    def authenticate(self, db, login, password):
        # Before calling /api/auth, call /web?db=*** otherwise web service is not found
        request.session.authenticate(db, login, password)
        return self.session_info(request)

    @http.route('/api/<string:model>', auth='user', methods=["GET"])
    @make_response()
    def search_read(self, model, **kwargs):
        eval_request_params(kwargs)
        return request.env[model].search_read(**kwargs)

    @http.route('/api/<string:model>/<int:id>', auth='user', methods=["GET"])
    @make_response()
    def read(self, model, id, **kwargs):
        eval_request_params(kwargs)
        result = request.env[model].browse(id).read(**kwargs)
        return result and result[0] or {}

    @http.route('/api/<string:model>', auth='user',
           methods=["POST"], csrf=False)
    @make_response()
    def create(self, model, **kwargs):
        eval_request_params(kwargs)
        return request.env[model].create(**kwargs).id

    @http.route('/api/<string:model>/<int:id>', auth='user',
           methods=["PUT"], csrf=False)
    @make_response()
    def write(self, model, id, **kwargs):
        eval_request_params(kwargs)
        return request.env[model].browse(id).write(**kwargs)

    @http.route('/api/<string:model>/<int:id>', auth='user',
           methods=["DELETE"], csrf=False)
    @make_response()
    def unlink(self, model, id):
        return request.env[model].browse(id).unlink()

    @http.route('/api/<string:model>/<int:id>/<string:method>', auth='user',
           methods=["PUT"], csrf=False)
    @make_response()
    def custom_method(self, model, id, method, **kwargs):
        eval_request_params(kwargs)
        record = request.env[model].browse(id)
        return getattr(record, method)(**kwargs)
