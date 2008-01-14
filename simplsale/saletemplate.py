from __future__ import with_statement

from copy import deepcopy
import csv
from os.path import abspath, join
from StringIO import StringIO

from lxml.cssselect import CSSSelector
from lxml.etree import HTML

from mako.template import Template

import pylons.config

from simplsale.lib import helpers as h


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

    def fields(self, required=False):
        """Returns a dictionary whose keys are the field names used in
        the `simplsale-form` form in the index document, and whose
        values are empty strings.

        Uses all fields if `required` is `False`, or only the required
        fields if `required` is `True`.
        """
        form = h.simplsale_form(self._index_xml)
        if required:
            required = '.required'
        else:
            required = ''
        elements = CSSSelector('input[type!="submit"]%s, select%s'
                               % (required, required))(form)
        names = []
        for e in elements:
            name = e.attrib.get('name', None)
            if name is not None:
                names.append(name)
        if 'billing_amount' in names and not required:
            names.extend(['billing_amount_price', 'billing_amount_name'])
        d = dict((key, '') for key in names)
        return d

    def index_xml(self):
        """Return a copy of the root XML element of the index
        document."""
        return deepcopy(self._index_xml)

    def success_xml(self):
        """Return a copy of the root XML element of the success
        document."""
        return deepcopy(self._success_xml)

    def _text(self, template, **kw):
        """Apply `kw` to the template and return the rendered text."""
        ns = dict()
        ns['csv'] = _args_to_csv
        ns['f'] = _Namespace(kw)
        return Template(template).render(**ns)

    def receipt_text(self, **kw):
        """Apply `kw` to the receipt template and return the rendered
        text."""
        return self._text(self._receipt_template, **kw)

    def record_text(self, **kw):
        """Apply `kw` to the record template and return the rendered
        text."""
        return self._text(self._record_template, **kw)


class _Namespace(object):

    def __init__(self, kw):
        self.__dict__.update(kw)


def _args_to_csv(*args):
    o = StringIO()
    w = csv.writer(o)
    w.writerow(args)
    return o.getvalue().strip()


