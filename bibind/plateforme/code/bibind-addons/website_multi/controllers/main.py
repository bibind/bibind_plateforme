import re
import datetime
import werkzeug
from openerp import tools
from openerp.addons.web import http
from openerp.http import request
from openerp.addons.website.controllers.main import Website
from openerp.addons.website.models.website import slug
from openerp.osv.orm import browse_record
import re
import logging
_logger = logging.getLogger('website controller')



class QueryURL(object):
    def __init__(self, path='', path_args=None, **args):
        self.path = path
        self.args = args
        self.path_args = set(path_args or [])

    def __call__(self, path=None, path_args=None, **kw):
        path = path or self.path
        for k, v in self.args.items():
            kw.setdefault(k, v)
        path_args = set(path_args or []).union(self.path_args)
        paths, fragments = [], []
        for key, value in kw.items():
            if value and key in path_args:
                if isinstance(value, browse_record):
                    paths.append((key, slug(value)))
                else:
                    paths.append((key, value))
            elif value:
                if isinstance(value, list) or isinstance(value, set):
                    fragments.append(werkzeug.url_encode([(key, item) for item in value]))
                else:
                    fragments.append(werkzeug.url_encode([(key, value)]))
        for key, value in paths:
            path += '/' + key + '/%s' % value
        if fragments:
            path += '?' + '&'.join(fragments)
        return path



class website_multi(Website):

    _bibindblog_post_per_page = 20
    _bibindpost_comment_per_page = 10

    @http.route('/', type='http', auth="public", website=True)
    def index(self, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        page = 'homepage'
        nom_domain = request.website.name
        main_menu = request.website.menu_id
        first_menu = main_menu.child_id and main_menu.child_id[0]
        _logger.info('main_menu : %s' % (main_menu))
        _logger.info('first_menu : %s' % (first_menu))
        _logger.info('first_menu : %s' % (first_menu.url))
        _logger.info('/ nom de domain : %s' % (nom_domain))
        _logger.info('/ first in : %s' % (first_menu.url.startswith(('/page/', '/?', '/#'))))
        
        if nom_domain=='bibind.com':
            page= 'bibind'
            
        if nom_domain=='freelance.bibind.com':
            page= 'cvbibind'
          
        if first_menu:
            if not (first_menu.url.startswith(('/page/', '/?', '/#')) or (first_menu.url == '/')):
                return request.redirect(first_menu.url)
            if first_menu.url.startswith('/page/'):
                return request.registry['ir.http'].reroute(first_menu.url)
        _logger.info('/ fin : %s' % (page))
        return self.page(page)

    @http.route('/website/add/<path:path>', type='http', auth="user", website=True)
    def pagenew(self, path, noredirect=False, add_menu=None):
        cr, uid, context = request.cr, request.uid, request.context

        xml_id = request.registry['website'].new_page(request.cr, request.uid, path, context=request.context)
        if add_menu:
            request.registry['website.menu'].create(cr, uid, {
                'name': path,
                'url': '/page/' + xml_id,
                'parent_id': request.website.menu_id.id,
                'website_id': request.website.id
            }, context=context)

        # Reverse action in order to allow shortcut for /page/<website_xml_id>
        url = "/page/" + re.sub(r"^website\.", '', xml_id)

        if noredirect:
            return werkzeug.wrappers.Response(url, mimetype='text/plain')

        return werkzeug.utils.redirect(url)
    
    def nav_list(self):
        blog_post_obj = request.registry['blog.post']
        groups = blog_post_obj.read_group(
            request.cr, request.uid, [], ['name', 'create_date'],
            groupby="create_date", orderby="create_date desc", context=request.context)
        for group in groups:
            begin_date = datetime.datetime.strptime(group['__domain'][0][2], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
            end_date = datetime.datetime.strptime(group['__domain'][1][2], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
            group['date_begin'] = '%s' % datetime.date.strftime(begin_date, tools.DEFAULT_SERVER_DATE_FORMAT)
            group['date_end'] = '%s' % datetime.date.strftime(end_date, tools.DEFAULT_SERVER_DATE_FORMAT)
        return groups
    
    
    @http.route('/page/<page:page>', type='http', auth="public", website=True)
    def page(self, page, **opt):
        values = {
            'path': page,
        }
        # /page/website.XXX --> /page/XXX
        if page.startswith('website.'):
            return request.redirect('/page/' + page[8:], code=301)
        elif '.' not in page:
            page = 'website.%s' % page

        try:
            request.website.get_template(page)
        except ValueError, e:
            # page not found
            if request.website.is_publisher():
                page = 'website.page_404'
            else:
                return request.registry['ir.http']._handle_exception(e, 404)

        values.update(self.get_list_actu(**opt))
        
        
        
        return request.render(page, values)    
    
    def get_list_actu(self, **opt):
        
        
        date_begin, date_end = opt.get('date_begin'), opt.get('date_end')
        cr, uid, context = request.cr, request.uid, request.context
        blog_post_obj = request.registry['blog.post']

        blog_obj = request.registry['blog.blog']
        blog = blog_obj.browse(cr, uid, [1], context=context)

        blog_ids = blog_obj.search(cr, uid, [], order="create_date asc", context=context)
        blogs = blog_obj.browse(cr, uid, blog_ids, context=context)

        domain = []
        
        domain += [('blog_id', '=', 1)]
       
        blog_url = QueryURL('', ['blog', 'tag'], blog=blog, date_begin=date_begin, date_end=date_end)
        post_url = QueryURL('', ['blogpost'],  date_begin=date_begin, date_end=date_end)

        blog_post_ids = blog_post_obj.search(cr, uid, domain, order="create_date desc", context=context)
        blog_posts = blog_post_obj.browse(cr, uid, blog_post_ids, context=context)
        page = 1
        pager = request.website.pager(
            url=blog_url(),
            total=len(blog_posts),
            page=1,
            step=self._bibindblog_post_per_page,
        )
        pager_begin = (page - 1) * self._bibindblog_post_per_page
        pager_end = page * self._bibindblog_post_per_page
        blog_posts = blog_posts[pager_begin:pager_end]

        tag_obj = request.registry['blog.tag']
        tag_ids = tag_obj.search(cr, uid, [], context=context)
        tags = tag_obj.browse(cr, uid, tag_ids, context=context)

        return {
            'blog': blog,
            'blogs': blogs,
            'tags': tags,
            
            'blog_posts': blog_posts,
            'pager': pager,
            'nav_list': self.nav_list(),
            'blog_url': blog_url,
            'post_url': post_url,
            'date': date_begin,
            'path': page,
        }
        
        



