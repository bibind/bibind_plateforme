# -*- coding: utf-8 -*-

from ConfigParser import SafeConfigParser
import codecs


class OdooRestConfig:

    def __init__(self, filename):
        self.config_parser = SafeConfigParser()
        # Open the file with the correct encoding
        with codecs.open(filename, 'r', encoding='utf-8') as f:
            self.config_parser.readfp(f)

    def get(self, attribute):
        return self.config_parser.get('options', attribute)

    def has_option(self, attribute):
        return self.config_parser.has_option('options', attribute)


config = OdooRestConfig('odoo_rest.conf')
