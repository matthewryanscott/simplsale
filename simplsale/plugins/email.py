from __future__ import absolute_import

import email


__all__ = [
    'InlineEmail',
    'MockEmail',
    'SendmailEmail',
    ]


class BaseEmail(object):

    def __init__(self, sale_template, values):
        self._sale_template = sale_template
        self._values = sale_template.fields()
        self._values.update(values)

    def apply_notice(self, element):
        element.text = 'We have emailed a receipt of this transaction to you.'

    def _receipt_record(self):
        """Return a tuple of `(receipt_text, record_text)` based on
        values given during construction."""
        return (
            self._sale_template.receipt_text(**self._values),
            self._sale_template.record_text(**self._values),
            )


class InlineEmail(BaseEmail):
    pass


class MockEmail(BaseEmail):

    receipts = []
    receipt_senders = []
    receipt_recipient_sets = []

    records = []
    record_senders = []
    record_recipient_sets = []

    def deliver(self):
        receipt_text, record_text = self._receipt_record()
        # Find the recipients and senders of each email.
        receipt_sender, receipt_recipients = sender_recipients(receipt_text)
        record_sender, record_recipients = sender_recipients(record_text)
        # Store in class-level queues.
        self.receipts.append(receipt_text)
        self.receipt_senders.append(receipt_sender)
        self.receipt_recipient_sets.append(receipt_recipients)
        self.records.append(record_text)
        self.record_senders.append(record_sender)
        self.record_recipient_sets.append(record_recipients)


class SendmailEmail(object):
    pass


def individual(addrs):
    if addrs:
        return set(s.strip() for s in addrs.split(','))
    else:
        return set()


def sender_recipients(email_text):
    """Return a tuple of (recipients_list, senders_list) based on the
    text of the given email."""
    msg = email.message_from_string(email_text)
    sender = msg['From']
    recipients = individual(msg['To'])
    cc_addrs = individual(msg['Cc'])
    bcc_addrs = individual(msg['Bcc'])
    recipients.update(cc_addrs)
    recipients.update(bcc_addrs)
    return (sender, recipients)
