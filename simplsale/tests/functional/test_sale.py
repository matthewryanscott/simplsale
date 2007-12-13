from datetime import date

from lxml.cssselect import CSSSelector
from lxml.etree import HTML, XPath, tounicode

from simplsale.tests import *

class TestSaleController(TestController):

    def _minimal_index(self):
        response = self.app.get(url_for(
            controller='sale',
            sale_template='minimal',
            ))
        # We get a 302 since url_for doesn't add the '/' to the end,
        # so follow it and get the actual index page.
        assert response.status == 302
        response = response.follow()
        return response

    def test_proper_document(self):
        """DTDs and so forth are properly output."""
        response = self._minimal_index()
        # DTD is in the body.
        assert 'http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd' in response.body
        # Empty scripts are closed by </script>, and not using <script ... />
        assert '></script>' in response.body

    def test_new_no_form_errors(self):
        """With new form, no form errors are present."""
        response = self._minimal_index()
        doc = HTML(response.body)
        selector = CSSSelector('#form-errors')
        assert selector(doc) == []
        
    def test_new_no_field_errors(self):
        """With new form, no field errors are present."""
        response = self._minimal_index()
        doc = HTML(response.body)
        for name in ['billing_email', 'billing_name', 'billing_street',
                     'billing_zip', 'billing_card_number',
                     'billing_expiration']:
            selector = CSSSelector('#%s-errors' % name)
            assert selector(doc) == []

    def test_new_expiration_field_values(self):
        """Expiration fields should contain valid values to select from."""
        response = self._minimal_index()
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
        response = self._minimal_index()
        # Partially fill in the form.
        form = response.forms[0]
        fields = form.fields
        fields['billing_amount'][0].value = '40.00 option 1'
        fields['billing_name'][0].value = 'Some Name'
        fields['billing_zip'][0].value = '90210'
        fields['billing_state'][0].value = 'CA'
        fields['billing_expiration_month'][0].value = '06'
        fields['billing_expiration_year'][0].value = '09'
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
                if name.startswith('billing_expiration'):
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
        # Check for lack of field errors for required fields with
        # values.
        def required_ok(**kw):
            for name, expected_value in kw.items():
                if name.startswith('billing_expiration'):
                    error_name = 'billing_expiration-errors'
                else:
                    error_name = name + '-errors'
                errors = CSSSelector('#' + error_name)(doc)
                assert len(errors) == 0
                field = form.fields[name][0]
                print name, field.value, expected_value
                assert field.value == expected_value
        required_ok(
            billing_amount = '40.00 option 1',
            billing_name = 'Some Name',
            billing_zip = '90210',
            # billing_state is not required
            billing_expiration_month = '06',
            billing_expiration_year = '09',
            )
