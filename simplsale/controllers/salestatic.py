import logging
import os

from paste.urlparser import StaticURLParser

from simplsale.lib.base import *
from simplsale.saletemplate import SaleTemplate

log = logging.getLogger(__name__)


_apps = {
    # html_path: static_app,
    }


def SalestaticController(environ, start_response):
    # Find the path for web resources.
    routes_dict = environ['pylons.routes_dict']
    path = routes_dict['path']
    sale_template = SaleTemplate(routes_dict['sale_template'])
    html_path = os.path.join(sale_template.path, 'html')
    # Find or create a static file serving app for this path.
    if html_path in _apps:
        app = _apps[html_path]
    else:
        app = StaticURLParser(html_path)
        _apps[html_path] = app
    # Call upon that app to serve the given path.
    environ['PATH_INFO'] = path
    return app(environ, start_response)
