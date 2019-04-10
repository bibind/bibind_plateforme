# -*- coding: utf-8 -*-
import odoorpc

from flask.ext.httpauth import HTTPBasicAuth
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from config import config

auth = HTTPBasicAuth()


class OdooUser:

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def set_id(self, id):
        self.id = id

    def generate_auth_token(self, expiration=600):
        s = Serializer(config.get('secret_key'), expires_in=expiration)
        return s.dumps({'id': self.id})

    def verify_password(self):
        server = config.get('odoo_server')
        database = config.get('odoo_db')
        self.odoo = odoorpc.ODOO(server, port=8069)
        self.odoo.login(database, self.username, self.password)
        if self.odoo:
            return True
        return False


class OdooAuth:

    def __init__(self):
        self.user_id = 0
        self.users = {}

    def add_user(self, user):
        self.user_id += 1
        user.set_id(self.user_id)
        self.users.update(
            {self.user_id: user})

    def remove_user(self, id):
        # TODO
        pass

    def get_user(self, id):
        return id in self.users and self.users[id]

    def get_user_by_name(self, username):
        for user in self.users:
            if user['username'] == username:
                return user
        return False

    def verify_auth_token(self, token):
        s = Serializer(config.get('secret_key'))
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        return self.get_user(data['id'])
