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
        print response.body
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
        
        # Submit the form.
        
        # Check form-errors for presence of error text.
        
        # Check field errors for presence of error text for required
        # fields with missing values.

        # Check for lack of field errors for required fields with
        # values.
