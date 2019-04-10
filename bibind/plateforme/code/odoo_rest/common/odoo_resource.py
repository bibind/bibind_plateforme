# -*- coding: utf-8 -*-
from flask_restful import Resource
from flask import g, request
from odoo_auth import auth
from pytz import timezone
import time
import pytz
from datetime import datetime


class OdooResource(Resource):

    odoo_model = False
    odoo_fields = []

    def dispatch_request(self, *args, **kwargs):
        self.method_decorators.append(auth.login_required)
        return super(OdooResource, self).dispatch_request(*args, **kwargs)

    def get(self, res_id=False):
        if not self.odoo_model:
            return {'Warning!': 'Model or Fields Undefined'}
        arguments = request.args
        if res_id:
            domain = [('id', '=', res_id)]
        elif 'domain' in arguments:
            domain = eval(request.args['domain'])
            # TODO Test its formed ok
        else:
            domain = []
        if 'offset' in arguments:
            offset = eval(request.args['offset'])
        else:
            offset = 0
        if 'limit' in arguments:
            limit = eval(request.args['limit'])
        else:
            limit = None
        if 'order' in arguments:
            order = eval(request.args['order'])
        else:
            order = None
        if 'context' in arguments:
            context = eval(request.args['context'])
        else:
            context = None
        proxy = g.user.odoo.env[self.odoo_model]
        items = proxy.search(
            domain,
            offset=offset,
            limit=limit,
            order=order,
            context=context)
        self.user_timezone = g.user.odoo.env.context['tz']
        if 'fields' in arguments:
            fields = request.args['fields']
            fields = (fields == 'all') and self.odoo_fields or eval(fields)
            return [items, fields]
        else:
            return [items, False]

    def post(self):
        arguments = request.get_json(force=True)
        proxy = g.user.odoo.env[self.odoo_model]
        res_id = proxy.create(arguments)
        return {'id': res_id}, 201

    def put(self, res_id):
        arguments = request.get_json(force=True)
        proxy = g.user.odoo.env[self.odoo_model]
        element = proxy.browse(int(res_id))
        res = element.write(arguments)
        return {'result': res}

    def delete(self, res_id):
        proxy = g.user.odoo.env[self.odoo_model]
        element = proxy.browse(int(res_id))
        res = element.unlink()
        return {'result': res}

    def correct_date(self, date):
        if self.user_timezone:
            correct_date = datetime.strptime(date,
                                             "%Y-%m-%d %H:%M:%S")
            tz = timezone(self.user_timezone)
            correct_date = pytz.utc.localize(correct_date).astimezone(tz)
            correct_date = correct_date.strftime("%Y-%m-%d %H:%M:%S")
            return correct_date
        else:
            return None
