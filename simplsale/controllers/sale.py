from datetime import date
import logging

from lxml.cssselect import CSSSelector
from lxml.etree import tounicode

import pkg_resources

from simplejson import loads

from ziplookup.data.zipcode import get_zipcode_info

from simplsale.lib.base import *
from simplsale.saletemplate import SaleTemplate

log = logging.getLogger(__name__)


XHTML11_DTD = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
               '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">')


class SaleController(BaseController):

    def index(self, sale_template):
        if request.method == 'GET' and not request.path_info.endswith('/'):
            # Require trailing slash to make relative paths work
            # right.
            #
            # XXX: More elegant way to do this with Pylons?
            h.redirect_to(request.path_info + '/')
        else:
            return self.index_slash(sale_template)

    def index_slash(self, sale_template):
        sale = SaleTemplate(sale_template)
        index_xml = sale.index_xml()
        self._apply_commerce_notice(index_xml)
        form = h.simplsale_form(index_xml)
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
        # GET-specific stuff.
        if request.method == 'GET':
            # Empty form, so remove the form-errors element.
            h.set_form_errors(form, None)
            # Also remove any field errors.
            field_names = sale.fields().keys()
            h.remove_field_errors(form, *field_names)
            h.remove_field_errors(form, 'billing_expiration')
        # POST-specific stuff.
        elif request.method == 'POST':
            # Get the values for all of the fields.
            values = {}
            for name in sale.fields().keys():
                values[name] = request.params.get(name, '').strip()
            # Check to make sure all required fields are filled in.
            values_ok = True
            zip_is_valid = True
            for name in sale.fields(required=True).keys():
                if name.startswith('billing_expiration_'):
                    continue
                value = values[name]
                if value == '':
                    # Set form errors if there are empty required
                    # fields.
                    values_ok = False
                elif name == 'billing_zip' and not h.is_valid_zip(value):
                    # Special handling for ZIP codes, to determine
                    # validity.
                    zip_is_valid = values_ok = False
                else:
                    # Remove field errors for non-empty required
                    # fields, and set their values to what the user
                    # gave.
                    h.remove_field_errors(form, name)
                h.set_field_value(form, name, value)
            # Handle billing_expiration_ differently.
            month = values['billing_expiration_month']
            year = values['billing_expiration_year']
            if month == '' or year == '':
                values_ok = False
            else:
                h.remove_field_errors(form, 'billing_expiration')
            h.set_field_value(form, 'billing_expiration_month', month)
            h.set_field_value(form, 'billing_expiration_year', year)
            # Resolve ZIP codes if optional city and state not
            # completely filled in.
            if (zip_is_valid
                and (values.get('billing_city', None) == ''
                     or values.get('billing_state', None) == ''
                     )):
                try:
                    info = loads(get_zipcode_info(str(values['billing_zip'])))
                except KeyError:
                    pass
                else:
                    values['billing_city'] = info['city']
                    values['billing_state'] = info['state']
                    h.set_field_value(form, 'billing_city', info['city'])
                    h.set_field_value(form, 'billing_state', info['state'])
            # Finish up.
            if values_ok:
                # Redirect to success page when everything is OK.
                # --- Unsanitized values ---
                ba_price, ba_name = values['billing_amount'].split(' ', 1)
                values['billing_amount_price'] = ba_price
                # Create and submit the commerce transaction.
                CommerceClass = config['simplsale.commerce.class']
                transaction = CommerceClass(config, values)
                transaction.submit()    # Blocking.
                # --- Sanitize ---
                values['billing_amount_name'] = ba_name
                values['billing_amount_price'] = ba_price
                # Obscure the card number.
                cn = values['billing_card_number']
                obscure_len = len(cn) - 4
                obscured_cn = ('*' * obscure_len) + cn[obscure_len:]
                values['billing_card_number'] = obscured_cn
                # --- Sanitized values ---
                if transaction.result is transaction.SUCCESS:
                    # Successful transaction, proceed to redirect to
                    # success page.
                    values['transaction_number'] = transaction.number
                    # Associate values with transaction number.
                    g.success_data[transaction.number] = values
                    # Perform the redirection.
                    h.redirect_to(h.url_for(
                        'sale_success',
                        sale_template=sale_template,
                        transaction_number=transaction.number,
                        ))
                elif transaction.result is transaction.FAILURE:
                    # Failed transaction, continue with index page.
                    h.set_form_errors(
                        form,
                        'We could not process your transaction. '
                        'Please make sure that the information '
                        'below is correct.  ("%s")' % transaction.result_text
                        )
            else:
                # Set form errors and continue with rendering the
                # index page again.
                h.set_form_errors(
                    form, 'Some fields are not complete.  See below.')
        return XHTML11_DTD + tounicode(index_xml, method='html')

    def success(self, sale_template, transaction_number):
        sale = SaleTemplate(sale_template)
        success_xml = sale.success_xml()
        self._apply_commerce_notice(success_xml)
        values = g.success_data[transaction_number]
        for key, value in values.items():
            for e in CSSSelector('#' + key)(success_xml):
                e.text = value
        return XHTML11_DTD + tounicode(success_xml, method='html')

    def _apply_commerce_notice(self, doc):
        notice = config['simplsale.commerce.class'].notice
        for e in CSSSelector('#simplsale-commerce-notice')(doc):
            e.text = notice
