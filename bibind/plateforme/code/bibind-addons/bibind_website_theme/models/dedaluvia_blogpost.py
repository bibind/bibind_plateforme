# -*- coding: utf-8 -*-

from datetime import datetime
import difflib
import lxml
import random

from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _



class DedaluviaBlogPost(osv.Model):
   
    _inherit = ['blog.post']

    _columns = {
        'description':fields.html('Description', translate=True, sanitize=False),
        'imageinstance_ids': fields.one2many('blog.postimage','imagemanager_id', 'List image'),
       }

    _defaults = {
      
          }

    
DedaluviaBlogPost()



class blogpostimage(osv.Model):
    _name = "blog.postimage"

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image, avoid_resize_medium=True)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': value}, context=context)
    
   
    
    _columns = {
        'name': fields.char('Name', required=True, translate=True, select=True),
        'image': fields.binary('image'),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={'blog.post': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),},),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={'blog.post': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),},),
        'description':fields.text('Description', required=True),
        'imagemanager_id': fields.many2one('blog.post', 'post', ondelete="cascade", required=True),
      }
   
   
    _defaults = {
     }

 
blogpostimage()
