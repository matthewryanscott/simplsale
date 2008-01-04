from __future__ import with_statement

import csv
from os.path import abspath, join
from StringIO import StringIO

from lxml.cssselect import CSSSelector
from lxml.etree import HTML

from mako.template import Template

import pylons.config

from simplsale.lib.helpers import field_names


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
                self._index_xml = HTML(f.read())
            with open(join(self.path, 'html', 'success.html'), 'rb') as f:
                self._success_xml = HTML(f.read())
            with open(join(self.path, 'receipt.txt'), 'rU') as f:
                self._receipt_template = f.read()
            with open(join(self.path, 'record.txt'), 'rU') as f:
                self._record_template = f.read()
        except IOError:
            raise KeyError('Template %r not found.' % name)

    def fields(self):
        # XXX move field_names and form finding to this class.
        form = CSSSelector('form#simplsale-form')(self._index_xml)[0]
        f = dict((key, '') for key in field_names(form))
        if 'billing_amount' in f:
            f.setdefault('billing_amount_price', '')
            f.setdefault('billing_amount_name', '')
        return f

    def index_form(self):
        """Return the XML element of the SimplSale form in the index."""
        return CSSSelector('form#simplsale-form')(self._index_xml)[0]

    def index_xml(self):
        """Return the root XML element of the index document."""
        return self._index_xml

    def success_xml(self):
        """Return the root XML element of the success document."""
        return self._success_xml

    def _text(self, template, **kw):
        """Apply `kw` to the template and return the rendered text."""
        kw['csv'] = _args_to_csv
        return Template(template).render(**kw)

    def receipt_text(self, **kw):
        """Apply `kw` to the receipt template and return the rendered
        text."""
        return self._text(self._receipt_template, **kw)

    def record_text(self, **kw):
        """Apply `kw` to the record template and return the rendered
        text."""
        return self._text(self._record_template, **kw)


def _args_to_csv(*args):
    o = StringIO()
    w = csv.writer(o)
    w.writerow(args)
    return o.getvalue().strip()
