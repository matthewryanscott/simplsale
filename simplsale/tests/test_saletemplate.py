from textwrap import dedent

from simplsale.saletemplate import SaleTemplate


class TestSaleTemplate(object):

    def setUp(self):
        self.minimal = SaleTemplate('minimal')

    def test_fields(self):
        expected = {
            'billing_amount': '',
            'billing_amount_price': '',
            'billing_amount_name': '',
            'billing_email': '',
            'billing_name': '',
            'billing_street': '',
            'billing_zip': '',
            'billing_city': '',
            'billing_state': '',
            'billing_card_number': '',
            'billing_expiration_month': '',
            'billing_expiration_year': '',
            'billing_cvv2': '',
            }
        print self.minimal.fields()
        assert expected == self.minimal.fields()

    def test_receipt_text_all(self):
        values = dict(
            billing_email = 'abc@example.com',
            transaction_number = '123',
            billing_amount = '45.00 some option',
            billing_amount_description = 'some option',
            billing_amount_price = '45.00',
            billing_street = '123 Fake St.',
            billing_city = 'Springfield',
            billing_state = 'OR',
            billing_zip = '97477',
            billing_card_number = '************5100',
            commerce_name = 'dummy',
            commerce_notice = '(No actual commerce plugin was used)',
            )
        expected = dedent("""\
            From: SimplSale-test@example.com
            To: abc@example.com
            Subject: SimplSale minimal - sale # 123

            (No actual commerce plugin was used)

            The SimplTest minimal sale completed.

            The transaction number is 123.

            You purchased "some option".
            Billing amount was 45.00.

            Details:

            Billing Street: 123 Fake St.
            Billing City: Springfield
            Billing State: OR
            Billing ZIP: 97477
            Billing Card No.: ************5100
            """)
        assert expected == self.minimal.receipt_text(**values)

    def test_record_text_all(self):
        values = dict(
            billing_email = 'abc@example.com',
            transaction_number = '123',
            billing_amount = '45.00 some option',
            billing_amount_description = 'some option',
            billing_amount_price = '45.00',
            billing_street = '123 Fake St.',
            billing_city = 'Springfield',
            billing_state = 'OR',
            billing_zip = '97477',
            billing_card_number = '************5100',
            commerce_name = 'dummy',
            commerce_notice = '(No actual commerce plugin was used)',
            )
        expected = dedent("""\
            From: SimplSale-test@example.com
            To: SimplSale-test@example.com
            Subject: SimplSale minimal [dummy] - 123

            Transaction number: 123
            Billing amount:     45.00 some option

            Billing email:      abc@example.com
            Billing Street:     123 Fake St.
            Billing City:       Springfield
            Billing State:      OR
            Billing ZIP:        97477
            Billing Card No.:   ************5100

            CSV-formatted:

            123,abc@example.com,45.00 some option,123 Fake St.,Springfield,OR,97477,************5100
            """)
        assert expected == self.minimal.record_text(**values)
