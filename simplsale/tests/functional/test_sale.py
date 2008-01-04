from datetime import date

from lxml.cssselect import CSSSelector
from lxml.etree import HTML, XPath, tounicode

from simplsale.plugins.commerce import MockCommerce
from simplsale.tests import *


EXP_YEAR = str(date.today().year + 1)[-2:]


class TestSaleController(TestController):

    def _index(self):
        response = self.app.get(url_for(
            controller = 'sale',
            template_name = 'minimal',
            ))
        # We get a 302 since url_for doesn't add the '/' to the end,
        # so follow it and get the actual index page.
        assert response.status == 302
        response = response.follow()
        return response

    def test_proper_document(self):
        """DTDs and so forth are properly output."""
        response = self._index()
        # DTD is in the body.
        assert 'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd' in response.body
        # Empty scripts are closed by </script>, and not using <script ... />
        assert '></script>' in response.body

    def test_commerce_notice(self):
        """Within unit tests, the banner for the 'mock' plugin appears
        on the index page."""
        response = self._index()
        doc = HTML(response.body)
        notices = CSSSelector('#simplsale-commerce-notice')(doc)
        assert len(notices) == 1
        assert notices[0].text == MockCommerce.notice

    def test_new_no_form_errors(self):
        """With new form, no form errors are present."""
        response = self._index()
        doc = HTML(response.body)
        selector = CSSSelector('#form-errors')
        assert selector(doc) == []
        
    def test_new_no_field_errors(self):
        """With new form, no field errors are present."""
        response = self._index()
        doc = HTML(response.body)
        for name in ['billing_email', 'billing_name', 'billing_street',
                     'billing_zip', 'billing_card_number',
                     'billing_expiration']:
            selector = CSSSelector('#%s-errors' % name)
            assert selector(doc) == []

    def test_new_expiration_field_values(self):
        """Expiration fields should contain valid values to select from."""
        response = self._index()
        form = response.forms[0]
        select_month = form.fields['billing_expiration_month'][0]
        assert select_month.options == [
            ('', True),                 # "(select)"
            ('01', False),
            ('02', False),
            ('03', False),
            ('04', False),
            ('05', False),
            ('06', False),
            ('07', False),
            ('08', False),
            ('09', False),
            ('10', False),
            ('11', False),
            ('12', False),
            ]
        this_year = str(date.today().year)[-2:]
        next_year = str(date.today().year + 1)[-2:]
        select_year = form.fields['billing_expiration_year'][0]
        options = select_year.options
        assert options[0] == ('', True) # "(select)"
        # This year is the first usable option.
        assert options[1] == (this_year, False)
        # There are several years following that.
        assert options[2] == (next_year, False)
        assert len(options) >= 5

    def test_post_empty_required_fields(self):
        """Empty values in required fields result in errors for those
        fields filled in, and returning the index page with a
        partially-complete form."""
        response = self._index()
        # Partially fill in the form.
        form = response.forms[0]
        fields = form.fields
        fields['billing_amount'][0].value = '40.00 option 1'
        fields['billing_name'][0].value = 'Some Name'
        fields['billing_zip'][0].value = '90210'
        fields['billing_state'][0].value = 'CA'
        fields['billing_expiration_month'][0].value = '06'
        # Submit the form.
        response = form.submit()
        form = response.forms[0]
        doc = HTML(response.body)
        # Check form-errors for presence of error text.
        form_errors = CSSSelector('#form-errors')(doc)
        assert len(form_errors) == 1
        assert form_errors[0].text != ''
        # Check field errors for presence of error text for required
        # fields with missing values.
        def required_empty(*args):
            for name in args:
                if name.startswith('billing_expiration_'):
                    error_name = 'billing_expiration-errors'
                else:
                    error_name = name + '-errors'
                errors = CSSSelector('#' + error_name)(doc)
                assert len(errors) == 1
                assert errors[0].text != ''
                field = form.fields[name][0]
                assert field.value == ''
        required_empty(
            'billing_email',
            'billing_street',
            # billing_city is not required
            'billing_card_number',
            )
        # In this case, since we treat the expiration differently for
        # the error field, look for the month having a value, the year
        # not having a value, and the error showing up.
        def has_errors_and_values(month, year):
            errors = CSSSelector('#billing_expiration-errors')(doc)
            assert len(errors) == 1
            assert errors[0].text != ''
            m = form.fields['billing_expiration_month'][0]
            assert m.value == month
            y = form.fields['billing_expiration_year'][0]
            assert y.value == year
        has_errors_and_values('06', '')
        # Fill in the year but not the month, and test again.
        form.fields['billing_expiration_month'][0].value = ''
        form.fields['billing_expiration_year'][0].value = EXP_YEAR
        response = form.submit()
        form = response.forms[0]
        doc = HTML(response.body)
        has_errors_and_values('', EXP_YEAR)
        # Check for lack of field errors for required fields with
        # values.
        def required_ok(**kw):
            for name, expected_value in kw.items():
                if name.startswith('billing_expiration_'):
                    error_name = 'billing_expiration-errors'
                else:
                    error_name = name + '-errors'
                errors = CSSSelector('#' + error_name)(doc)
                assert len(errors) == 0
                field = form.fields[name][0]
                assert field.value == expected_value
        required_ok(
            billing_amount = '40.00 option 1',
            billing_name = 'Some Name',
            billing_zip = '90210',
            # billing_state is not required
            )

    def test_post_bad_zipcode(self):
        """When a ZIP code is given that is not five digits, the form
        is shown again and the ZIP code field shows an error."""
        response = self._index()
        form = response.forms[0]
        # Fill in all required fields.
        form.fields['billing_amount'][0].value = '40.00 option 1'
        form.fields['billing_email'][0].value = 'foo@bar.com'
        form.fields['billing_name'][0].value = 'name o. card'
        form.fields['billing_street'][0].value = '123 fake st'
        form.fields['billing_zip'][0].value = '8230'
        form.fields['billing_card_number'][0].value = '5105105105105100'
        form.fields['billing_expiration_month'][0].value = '06'
        form.fields['billing_expiration_year'][0].value = EXP_YEAR
        # Submit it and check for errors.
        response = form.submit()
        form = response.forms[0]
        doc = HTML(response.body)
        # Check form-errors for presence of error text.
        form_errors = CSSSelector('#form-errors')(doc)
        assert len(form_errors) == 1
        assert form_errors[0].text != ''
        # Check ZIP code for presence of error text.
        zip_errors = CSSSelector('#billing_zip-errors')(doc)
        assert len(zip_errors) == 1
        assert zip_errors[0].text != ''

    def test_post_lookup_city_state_on_empty_zip(self):
        """When a ZIP code is given, but optional city and state
        fields are not given, those fields adopt values looked up from
        the ZipLookup database."""
        response = self._index()
        form = response.forms[0]
        # Fill in all required fields.
        form.fields['billing_zip'][0].value = '98240'
        # Submit it and check for filled-in city and state.
        response = form.submit()
        form = response.forms[0]
        def check_form():
            assert form.fields['billing_city'][0].value == 'Custer'
            assert form.fields['billing_state'][0].value == 'WA'
        check_form()
        # Blank out the city, change the state, then resubmit.  Should
        # resolve ZIP code again.
        form.fields['billing_city'][0].value = ''
        form.fields['billing_state'][0].value = 'NY'
        response = form.submit()
        form = response.forms[0]
        check_form()
        # This time, blank out the state and change the city.
        form.fields['billing_city'][0].value = 'Anytown'
        form.fields['billing_state'][0].value = ''
        response = form.submit()
        form = response.forms[0]
        check_form()

    def test_post_commerce_success(self):
        """When valid values are POST-ed, and the commercial
        transaction succeeds, redirect to the success page for the
        transaction."""
        response = self._index()
        form = response.forms[0]
        # Fill in all required fields.
        form.fields['billing_amount'][0].value = '40.00 option 1'
        form.fields['billing_email'][0].value = 'foo@bar.com'
        form.fields['billing_name'][0].value = 'name o. card'
        form.fields['billing_street'][0].value = '123 fake st'
        form.fields['billing_zip'][0].value = '90210'
        form.fields['billing_card_number'][0].value = '5105105105105100'
        form.fields['billing_expiration_month'][0].value = '06'
        form.fields['billing_expiration_year'][0].value = EXP_YEAR
        form.fields['billing_cvv2'][0].value = '123'
        # Submit it and assume a redirection.
        response = form.submit()
        assert response.status == 302
        response = response.follow()
        doc = HTML(response.body)
        # Look for the signs of success.
        def text(id):
            return CSSSelector('#' + id)(doc)[0].text
        assert text('transaction_number') != ''
        assert text('billing_amount_name') == 'option 1'
        assert text('billing_amount_price') == '40.00'
        assert text('billing_email') == 'foo@bar.com'
        assert text('billing_street') == '123 fake st'
        assert text('billing_city') == 'Beverly Hills'
        assert text('billing_state') == 'CA'
        assert text('billing_zip') == '90210'
        assert text('billing_card_number') == '************5100'

    def test_post_commerce_failure(self):
        """When valid values are POST-ed, but the commercial
        transaction fails, the form is shown again with an error
        message regarding the failure."""
        response = self._index()
        form = response.forms[0]
        # Fill in all required fields.
        form.fields['billing_amount'][0].value = '40.00 option 1'
        form.fields['billing_email'][0].value = 'foo@bar.com'
        form.fields['billing_name'][0].value = 'name o. card'
        form.fields['billing_street'][0].value = '123 fake st'
        form.fields['billing_zip'][0].value = '98230'
        form.fields['billing_card_number'][0].value = '5105105105105100'
        form.fields['billing_expiration_month'][0].value = '06'
        # XXX: Cheat, pretend that we're the robot we are, and add 01
        # as an option.
        form.fields['billing_expiration_year'][0].options.append(('01', False))
        form.fields['billing_expiration_year'][0].value = '01' # In the past.
        # Submit it and check for errors.
        response = form.submit()
        assert response.status == 200
        form = response.forms[0]
        doc = HTML(response.body)
        # Check form-errors for presence of error text.
        form_errors = CSSSelector('#form-errors')(doc)
        assert len(form_errors) == 1
        assert form_errors[0].text != ''

#     def test_post_success_persists(self):
#         """When a transaction succeeds, the success page is shown at a
#         unique URL that may be retrieved by GET-ing the same URL
#         again."""

#     def test_post_success_expires(self):
#         """Success pages eventually expire after a number of seconds."""
