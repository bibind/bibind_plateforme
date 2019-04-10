import werkzeug
import string
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
import json
import xml.etree.ElementTree as ET
import openerp.addons.website_sale.controllers.main
from ovh import api_ovh
import logging
_logger = logging.getLogger('Controller_Dedaluvia ')

PPG = 1  # Products Per Page
PPR = 1  # Products Per Row

class table_compute(object):
    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        for p in products:
            x = min(max(p.website_size_x, 1), PPR)
            y = min(max(p.website_size_y, 1), PPR)
            if index > PPG:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % PPR, pos / PPR, x, y):
                pos += 1

            if index > PPG and (pos / PPR) > maxy:
                break

            if x == 1 and y == 1:  # simple heuristic for CPU optimization
                minpos = pos / PPR

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos / PPR) + y2][(pos % PPR) + x2] = False
            self.table[pos / PPR][pos % PPR] = {
                'product': p, 'x':x, 'y': y,
                'class': " ".join(map(lambda x: x.html_class or '', p.website_style_ids))
            }
            if index <= PPG:
                maxy = max(maxy, y + (pos / PPR))
            index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows

        # TODO keep with input type hidden


class QueryURL(object):
    def __init__(self, path='', **args):
        self.path = path
        self.args = args

    def __call__(self, path=None, **kw):
        if not path:
            path = self.path
        for k, v in self.args.items():
            kw.setdefault(k, v)
        l = []
        for k, v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k, i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k, v)]))
        if l:
            path += '?' + '&'.join(l)
        return path





class website_sale(openerp.addons.website_sale.controllers.main.website_sale):
    
    @http.route(['/configuration/<model("sale.quote.template"):sale_quote_template_id>',
                 '/configuration/<model("sale.quote.template"):sale_quote_template_id>/page/<int:page>'], type='http', auth="public", website=True)
    def configProduct(self, sale_quote_template_id, page=0, **post):
        
       
        #=======================================================================
        # A chaque requete dune configuration dun devis correspondant
        # on verifie qu'il n'y pa  de devis en cours . Sinon on le vide
        # et On met en session le model quote template
        #=======================================================================
        
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        _logger.info('attr list  %s' % (request.session.get('sale_quote_id')))
        sale_quote_id = request.session.get('sale_quote_id')
        if sale_quote_id == None:
            request.session['sale_quote_id'] = sale_quote_template_id.id
        elif sale_quote_id != sale_quote_template_id.id :
                if request.session['sale_order_id'] == None :
                    request.session['sale_quote_id'] = sale_quote_template_id.id
                elif request.session['sale_order_id'] != False :
                        self.OrderReset(request.session['sale_order_id'], sale_quote_template_id)
                        request.session['sale_quote_id'] = sale_quote_template_id.id
            
        products_ids = []
        products_tmpl_ids = []
        products_tmpl_ids_ids = []
        quote_template = pool.get('sale.quote.template').browse(cr, SUPERUSER_ID, sale_quote_template_id.id)
        quote_line_quote = pool.get('sale.quote.line')
        
        for line in quote_template.quote_line:
            products_ids.append(line.product_id.id)
            products_tmpl_ids.append(line.product_id.product_tmpl_id)
            products_tmpl_ids_ids.append(line.product_id.product_tmpl_id.id)
            
        
        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = int(pricelist)
        else:
            pricelist = pool.get('product.pricelist').browse(cr, SUPERUSER_ID, context['pricelist'], context)

        product_obj = pool.get('product.template')
        products = []
        for product_id in products_tmpl_ids_ids:
            _logger.info(' product_id %s' % (product_id))
            context.update(active_id=product_id)
            product = product_obj.browse(cr, SUPERUSER_ID, product_id, context)
            products.append(product)
        
        product_count = len(products_ids)
        url = "/configuration/%s" % slug(sale_quote_template_id)
        pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        
        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        
        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, SUPERUSER_ID, [], context=context)
        styles = style_obj.browse(cr, SUPERUSER_ID, style_ids, context=context)
        
        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, SUPERUSER_ID, from_currency, to_currency, price, context=context)
        _logger.info('website checkout attr value %s' % (attrib_values))
        values = {
            'pager': pager,
            'pricelist': pricelist,
            'attrib_values': attrib_values,
            'products': products,
            'bins': table_compute().process(products),
            'rows': PPR,
            'styles': styles,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'compute_currency': compute_currency,
            'get_attribute_value_ids': self.get_attribute_value_ids
             }
        
        return request.website.render("dedaluvia_website_checkout.orderproducts", values)

    def OrderReset(self, sale_order_id, sale_quote_template_id):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
         
        sale_order_obj = pool['sale.order']
        sale_order = sale_order_obj.browse(cr, SUPERUSER_ID, sale_order_id, context=context)
        sol = pool.get('sale.order.line')
       
        for line in sale_order.order_line :
             sol.unlink(cr, SUPERUSER_ID, [line.id], context=context)
        
        return True
       
    @http.route(['/configuration/update_option'], type='http', auth="public", methods=['POST'], website=True)
    def cart_domain_options_update_json(self, product_id, add_qty=0, set_qty=1, goto_shop=None, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        _logger.info('website product_id debut %s' % (product_id))
        product_ids = product_id.split(",")
        _logger.info('website product_id debut %s' % (product_id))
        if (len(product_ids)>1):
            _logger.info('website product_id debut %s' % (product_id))
            line_ids = {}
            line_ids['product_id']=[]
            line_ids['line_id']=[]
            k = 0
            for product_id in product_ids:
                _logger.info('website product_id debut %s' % (product_id))
                
                
                order = request.website.sale_get_order(force_create=1)
                product = pool['product.product'].browse(cr, uid, int(product_id), context=context)
                _logger.info('cherche les param value %s' % (kw))
              
             
        
                option_ids = [p.id for tmpl in product.optional_product_ids for p in tmpl.product_variant_ids]
                optional_product_ids = []
                for k, v in kw.items():
                    if "optional-product-" in k and int(kw.get(k.replace("product", "add"))) and int(v) in option_ids:
                        optional_product_ids.append(int(v))
        
                value = {}
                if add_qty or set_qty:
                    value = order._cart_domain_update(product_id=int(product_id),
                        add_qty=int(add_qty), set_qty=int(set_qty),
                        kw =kw,
                        optional_product_ids=optional_product_ids)
        
                # options have all time the same quantity
                for option_id in optional_product_ids:
                    order._cart_domain_update(product_id=option_id,
                        set_qty=value.get('quantity'),
                        linked_line_id=value.get('line_id'))
                lndid =value.get('line_id')
                line_ids['product_id'].append( product_id)
                line_ids['line_id'].append( lndid)
                #line_ids[k] =json.dumps( {'product_id':product_id,'line_id': value.get('line_id'), 'quantity': str(order.cart_quantity)})
                k =k+1
        
        order = request.website.sale_get_order()
        line_ids['quantity']=str(order.cart_quantity)
        return  json.dumps(line_ids)
    
    
    def cart_multi_domain_options_update_json(self, product_id, add_qty=0, set_qty=1, **kw):
        
        order = request.website.sale_get_order(force_create=1)
        product = pool['product.product'].browse(cr, uid, int(product_id), context=context)
        _logger.info('cherche les param value %s' % (kw))
      
     

        option_ids = [p.id for tmpl in product.optional_product_ids for p in tmpl.product_variant_ids]
        optional_product_ids = []
        for k, v in kw.items():
            if "optional-product-" in k and int(kw.get(k.replace("product", "add"))) and int(v) in option_ids:
                optional_product_ids.append(int(v))

        value = {}
        if add_qty or set_qty:
            value = order._cart_domain_update(product_id=int(product_id),
                add_qty=int(add_qty), set_qty=int(set_qty),
                kw =kw,
                optional_product_ids=optional_product_ids)

        # options have all time the same quantity
        for option_id in optional_product_ids:
            order._cart_domain_update(product_id=option_id,
                set_qty=value.get('quantity'),
                linked_line_id=value.get('line_id'))

       
        return json.dumps( {'product_id':product_id,'line_id': value.get('line_id'), 'quantity': str(order.cart_quantity)})
    
    
    
    
    
    @http.route(['/configuration/update'], type='json', auth="public", methods=['POST'], website=True)
    def remove_line_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        order = request.website.sale_get_order(force_create=1)
        value = order._remove_line(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)
        
        return None
    
    @http.route(['/configuration/check_old_domain'], type='http', auth="public", methods=['POST'], website=True)
    def check_old_domain(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        _logger.info('json %s' % (kw))
        fr = json.dumps(kw)
       
        dat =json.loads(fr);
        sortid = kw.get('sort[id]')

        domain =kw.get('domain')
        tree = ET.parse('/opt/recette_odoo-addons/dedaluvia_website_checkout/controllers/extension.xml')
        root = tree.getroot()
        data ={}
        for key in dat:
            if type(key) in (tuple, list):
                 _logger.info('list?  %s' % (key))
                
            data[key] =dat.get(key)
            _logger.info('dat dat  %s' % (key))
            _logger.info('dat dat  %s' % (dat.get(key)))
       
        if not sortid ==None:
            data['sort']={}
            data['sort']['id']=sortid
        data['rows'] = []
        k = 0
        for child in root:
            data['rows'].append({'id':k,'did': int(child.attrib.get('id')),'price': child.attrib.get('price'),'categorie': child.attrib.get('categorie'), 'domain': domain+'.'+child.attrib.get('extension'),'extension':child.attrib.get('extension')})
            k = k+1
        
        data['rows']=sorted(data['rows'], key=lambda rows:rows['did'])
        data['total'] = k
        #data = json.dumps(data)
       
        
            
        return json.dumps(data, sort_keys=False)
    
    @http.route(['/configuration/check_domain_extension'], type='http', auth="public", methods=['POST'], website=True)
    def check_domain(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        
        fr = json.dumps(kw)
        dat =json.loads(fr);
        sortdid = kw.get('sort[did]')
        domain =kw.get('domain')
        with open('/opt/recette_odoo-addons/dedaluvia_website_checkout/controllers/dataAll-01.json') as data_file:    
            data = json.load(data_file)
        
        for key in data['rows'] :
            key['domain'] = domain+'.'+key['extension'] 
        
        for key in dat:
            data[key] =dat.get(key)
           
       
        if not sortdid ==None:
            data['sort']={}
            data['sort']['did']=sortdid
            _logger.info(sorted(data['rows'], key=lambda rows:rows['did']))
            data['rows']=sorted(data['rows'], key=lambda rows:rows['did'])

        data['rows']=sorted(data['rows'], key=lambda rows:rows['did'])
        #data = json.dumps(data)
        return json.dumps(data)
    
    
    @http.route(['/configuration/check_domain_available'], type='http', auth="public", methods=['POST'], website=True)
    def check_domain_availaible(self, **kw):
        rowid =  kw.get('rowid')
        domain = kw.get('domain')
        apiovh = api_ovh()
        data ={}
        data['rowid']=rowid
        check = apiovh.domain_check(domain)
        data['check']= check
        data = json.dumps(data)
        return data


        
   