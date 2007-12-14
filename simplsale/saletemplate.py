from __future__ import with_statement

from os.path import abspath, join

import pylons.config


_cache = {
    # absolute path: SaleTemplate instance,
    }


class SaleTemplate(object):

    def __new__(cls, name):
        """Return a new or cached SaleTemplate."""
        sale_template_dir = abspath(
            pylons.config['simplsale.sale_template_dir'])
        path = join(sale_template_dir, name)
        if path in _cache:
            return _cache[path]
        else:
            template = object.__new__(SaleTemplate)
            template.path = path
            _cache[path] = template
            return template

    def __init__(self, name):
        self.name = name
        # Read the source of the template files right away.
        try:
            with open(join(self.path, 'html', 'index.html'), 'rb') as f:
                self._index_html = f.read()
            with open(join(self.path, 'html', 'success.html'), 'rb') as f:
                self._success_html = f.read()
            with open(join(self.path, 'receipt.txt'), 'rU') as f:
                self._receipt_txt = f.read()
            with open(join(self.path, 'record.txt'), 'rU') as f:
                self._record_txt = f.read()
        except IOError:
            raise KeyError('Template %r not found.' % name)

    def index(self):
        return self._index_html

    def success(self):
        return self._success_html
