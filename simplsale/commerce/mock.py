from datetime import date
from random import randint

CUR_CENTURY_YEAR = date.today().year % 100


class MockCommerce(object):

    notice = 'You are using the SimplSale "mock" commerce plugin.'

    SUCCESS = 0
    FAILURE = 1

    def __init__(self, config, values):
        """Create a new mock commerce object."""
        # We don't have any configuration options, so skip that.
        self.values = values
        self.submitted = False

    def submit(self):
        if self.submitted:
            raise RuntimeError('Cannot re-submit %r.' % self)
        self.submitted = True
        if (int(self.values['billing_expiration_year']) < CUR_CENTURY_YEAR
            or self.values['billing_card_number'] == '4014014014014011'
            ):
            # XXX: Update this in 2100.  I'm sure Payflow Pro will be
            # quite different by then, too.
            self.result = self.FAILURE
            self.result_text = 'General failure.'
        else:
            self.result = self.SUCCESS
            self.result_text = 'Successful transaction.'
            self.number = str(randint(1000000, 9999999))
