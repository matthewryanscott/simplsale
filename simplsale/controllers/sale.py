from datetime import date
import logging

from lxml.cssselect import CSSSelector
from lxml.etree import HTML, tounicode

from simplsale.lib.base import *
from simplsale.saletemplate import SaleTemplate

log = logging.getLogger(__name__)


XHTML11_DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">'


class SaleController(BaseController):

    def index(self, sale_template):
        if request.method == 'GET' and not request.path_info.endswith('/'):
            # Require trailing slash to make relative paths work
            # right.
            #
            # XXX: More elegant way to do this with Pylons?
            h.redirect_to(request.path_info + '/')
        else:
            return self._index(sale_template)

    def _index(self, sale_template):
        sale = SaleTemplate(sale_template)
        doc = HTML(sale.index())
        form = CSSSelector('form#simplsale-form')(doc)[0]
        if request.method == 'GET':
            # Empty form, so remove the form-errors element.
            h.set_form_errors(form, None)
            # Also remove any field errors.
            # XXX: Only removes required fields at the moment.
            h.update_field_errors(form, {})
            # Fill in the expiration month and year fields if they use
            # select tags.
            month_selects = CSSSelector(
                'select[name="billing_expiration_month"]')(form)
            for select in month_selects:
                h.fill_in_expiration_months(select)
            year_selects = CSSSelector(
                'select[name="billing_expiration_year"]')(form)
            for select in year_selects:
                h.fill_in_expiration_years(select)
            # Done.
            return XHTML11_DTD + tounicode(doc, method='html')
        elif request.method == 'POST':
            pass

    def success(self, sale_template, transaction_number):
        return 'success %s %s' % (sale_template, transaction_number)
