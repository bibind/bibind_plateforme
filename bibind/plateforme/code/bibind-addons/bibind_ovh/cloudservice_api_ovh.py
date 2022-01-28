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
#Domaine ovh api 

# GET /domain List available services
# GET /domain/zone List available services
# GET /domain/zone/{zoneName} Get this object properties
# GET /domain/zone/{zoneName}/dnssec Get this object properties
# POST /domain/zone/{zoneName}/dnssec Enable Dnssec
# DELETE /domain/zone/{zoneName}/dnssec Disable Dnssec
# GET /domain/zone/{zoneName}/dynHost/login DynHost' logins
# POST /domain/zone/{zoneName}/dynHost/login Create a new DynHost login
# GET /domain/zone/{zoneName}/dynHost/login/{login} Get this object properties
# PUT /domain/zone/{zoneName}/dynHost/login/{login} Alter this object properties
# DELETE /domain/zone/{zoneName}/dynHost/login/{login} Delete a DynHost login
# POST /domain/zone/{zoneName}/dynHost/login/{login}/changePassword Change password of the DynHost login
# GET /domain/zone/{zoneName}/dynHost/record DynHost' records
# POST /domain/zone/{zoneName}/dynHost/record Create a new DynHost record
# GET /domain/zone/{zoneName}/dynHost/record/{id} Get this object properties
# PUT /domain/zone/{zoneName}/dynHost/record/{id} Alter this object properties
# DELETE /domain/zone/{zoneName}/dynHost/record/{id} Delete a DynHost record
# GET /domain/zone/{zoneName}/export Export zone
# POST /domain/zone/{zoneName}/import Beta Import zone
# GET /domain/zone/{zoneName}/record Records of the zone
# POST /domain/zone/{zoneName}/record Create a new resource record
# GET /domain/zone/{zoneName}/record/{id} Get this object properties
# PUT /domain/zone/{zoneName}/record/{id} Alter this object properties
# DELETE /domain/zone/{zoneName}/record/{id} Delete a resource record
# GET /domain/zone/{zoneName}/redirection Redirections
# POST /domain/zone/{zoneName}/redirection Create a new redirection
# GET /domain/zone/{zoneName}/redirection/{id} Get this object properties
# PUT /domain/zone/{zoneName}/redirection/{id} Alter this object properties
# DELETE /domain/zone/{zoneName}/redirection/{id} Delete a redirection
# POST /domain/zone/{zoneName}/refresh Refresh zone
# GET /domain/zone/{zoneName}/serviceInfos Beta Get this object properties
# PUT /domain/zone/{zoneName}/serviceInfos Beta Alter this object properties
# GET /domain/zone/{zoneName}/soa Get this object properties
# PUT /domain/zone/{zoneName}/soa Alter this object properties
# GET /domain/zone/{zoneName}/task Domain pending tasks
# GET /domain/zone/{zoneName}/task/{id} Get this object properties
# GET /domain/{serviceName} Get this object properties
# PUT /domain/{serviceName} Alter this object properties
# GET /domain/{serviceName}/authInfo Return authInfo code if the domain is unlocked
# GET /domain/{serviceName}/nameServer List of current name servers
# POST /domain/{serviceName}/nameServer Add new name server
# GET /domain/{serviceName}/nameServer/{id} Get this object properties
# DELETE /domain/{serviceName}/nameServer/{id} Delete a name server
# GET /domain/{serviceName}/owo List of whois obfuscators
# POST /domain/{serviceName}/owo Add whois obfuscators
# GET /domain/{serviceName}/owo/{field} Get this object properties
# DELETE /domain/{serviceName}/owo/{field} Delete a whois obfuscator
# GET /domain/{serviceName}/serviceInfos Beta Get this object properties
# PUT /domain/{serviceName}/serviceInfos Beta Alter this object properties
# GET /domain/{serviceName}/task Domain pending tasks
# GET /domain/{serviceName}/task/{id} Get this object properties
############################################################################







from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time, os, random, string
from openerp import pooler
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
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
import ovh

from ovhcli.utils import camel_to_snake
from ovhcli.schema import load_schemas, SCHEMAS_BASE_PATH, SCHEMAS
from ovhcli.formater import formaters, get_formater
from ovhcli.parser import ArgParser
from ovhcli.parser import ArgParserException, ArgParserTypeConflict, ArgParserUnknownRoute

try:
    import cPickle as pickle
except ImportError:
    import pickle

from ovh.client import ENDPOINTS

## parser
import requests

from socket import getaddrinfo

_logger = logging.getLogger("dedaluvia_cloudservice")

