from __future__ import absolute_import

import email
import smtplib

from lxml.etree import Element

import pylons.config


__all__ = [
    'InlineEmail',
    'MockEmail',
    'SendmailEmail',
    ]


class BaseEmail(object):

    def __init__(self, sale_template, new_values):
        values = sale_template.fields()
        values.update(new_values)
        # Keep track of receipt and record text, sender, total 
        # recipient set, and to/cc recipient set.
        self.receipt_text = sale_template.receipt_text(**values)
        self.record_text = sale_template.record_text(**values)
        # Find the recipients and senders of each email.
        (self.receipt_sender, 
         self.receipt_recipients,
         self.receipt_to_cc,
         ) = sender_recipients(self.receipt_text)
        (self.record_sender,
         self.record_recipients,
         self.record_to_cc,
         ) = sender_recipients(self.record_text)

    def apply_notice(self, element):
        p = Element('p')
        p.text = 'An email receipt was sent to these addresses:'
        ul = Element('ul')
        for address in sorted(self.receipt_to_cc):
            li = Element('li')
            li.text = address
            ul.append(li)
        element.extend([p, ul])

    def deliver(self):
        raise NotImplementedError()


class InlineEmail(BaseEmail):

    def deliver(self):
        # We don't actually do anything to deliver email in this plugin.
        pass

    def apply_notice(self, element):
        # Instead of showing who should receive the receipt, show
        # the full text of each email instead.
        receipt_header = Element('span')
        receipt_header.text = 'Text of receipt:'
        receipt_text = Element('pre')
        receipt_text.text = self.receipt_text
        record_header = Element('span')
        record_header.text = 'Text of record:'
        record_text = Element('pre')
        record_text.text = self.record_text
        element.extend([
            Element('hr'),
            receipt_header,
            receipt_text,
            Element('hr'),
            record_header,
            record_text,
            ])


class MockEmail(BaseEmail):

    def apply_notice(self, element):
        # We only use this for simple tests, so don't do anything fancier
        # than adding some text to the element.
        element.text = 'No actual email was sent.'

    def deliver(self):
        # Keep a class-level record of the last delivery.
        MockEmail.last_receipt_text = self.receipt_text
        MockEmail.last_receipt_sender = self.receipt_sender
        MockEmail.last_receipt_recipients = self.receipt_recipients
        MockEmail.last_receipt_to_cc = self.receipt_to_cc
        MockEmail.last_record_text = self.record_text
        MockEmail.last_record_sender = self.record_sender
        MockEmail.last_record_recipients = self.record_recipients
        MockEmail.last_record_to_cc = self.record_to_cc


class SmtpEmail(BaseEmail):
    
    def deliver(self):
        # Connect to the SMTP server.
        smtp_server = pylons.config['simplsale.email.server']
        server = smtplib.SMTP(smtp_server)
        # Send receipt.
        server.sendmail(
            self.receipt_sender, self.receipt_recipients, self.receipt_text)
        # Send record.
        server.sendmail(
            self.record_sender, self.record_recipients, self.record_text)
        # Done.
        server.quit()


def individual(addrs):
    if addrs:
        return set(s.strip() for s in addrs.split(','))
    else:
        return set()


def sender_recipients(email_text):
    """Return a tuple of (sender, recipients_list, to_cc_list) based on 
    the text of the given email."""
    msg = email.message_from_string(email_text)
    sender = msg['From']
    recipients = individual(msg['To'])
    cc_addrs = individual(msg['Cc'])
    bcc_addrs = individual(msg['Bcc'])
    recipients.update(cc_addrs)
    to_cc = recipients.copy()
    recipients.update(bcc_addrs)
    return (sender, recipients, to_cc)
