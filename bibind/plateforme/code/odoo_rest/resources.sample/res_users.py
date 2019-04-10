# -*- coding: utf-8 -*-
from ..common.odoo_resource import OdooResource
from ..common.odoo_rest import api


class ResUsers(OdooResource):

    odoo_model = 'res.users'
    odoo_fields = [
        'name',
        'login'
    ]


class ResUsersList(ResUsers):
    pass

api.add_resource(ResUsersList, '/res_users')
api.add_resource(ResUsers, '/res_users/<res_id>')
