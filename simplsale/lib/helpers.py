"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
import datetime

from lxml.cssselect import CSSSelector
from lxml.etree import Element

from webhelpers import *


def fill_in_expiration_months(select):
    """Fill in expiration date month values in the given `select` element.

    XXX: doctest
    """
    # First remove any children since they are just there to
    # help preview templates.
    for child in select.getchildren():
        select.remove(child)
    # Create the empty value option, selected since the form
    # is empty.
    e = Element('option', value='', selected='selected')
    e.text = '(select)'
    select.append(e)
    # Create months.
    for index, month_name in enumerate([
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November',
        'December',
        ]):
        month_number = index + 1
        e = Element('option', value='%02i' % month_number)
        e.text = '%02i (%s)' % (month_number, month_name)
        select.append(e)


def fill_in_expiration_years(select):
    """Fill in expiration date year values in the given `select` element.

    XXX: doctest
    """
    # Remove existing children as above.
    for child in select.getchildren():
        select.remove(child)
    # Create the empty value option, selected since the form
    # is empty.
    e = Element('option', value='', selected='selected')
    e.text = '(select)'
    select.append(e)
    # Create options for 10 years, starting from this year.
    this_year = datetime.date.today().year
    for year in range(this_year, this_year + 10):
        year_abbrev = str(year)[-2:]
        e = Element('option', value=year_abbrev)
        e.text = '%s (%s)' % (year_abbrev, year)
        select.append(e)


def set_form_errors(form, error_text):
    """Set the form-errors element's text in the form.

    XXX: doctest
    """
    form_errors = CSSSelector('#form-errors')(form)
    if error_text is None:
        # Remove form-errors if there is no error to report.
        for e in form_errors:
            e.getparent().remove(e)
    else:
        # Fill in form-errors with the text to report.
        for e in form_errors:
            # First get rid of anything lurking in the template.
            for c in e.getchildren():
                e.remove(c)
            # Now set the text.
            e.text = error_text


def field_names(form):
    """Return the names of all of the fields in `form`.

    Takes care to provide a `billing_expiration` name if both the
    month and year fields are present for that field.

    XXX: doctest
    """
    elements = CSSSelector('input[type!="submit"], select')(form)
    names = []
    for e in elements:
        name = e.attrib.get('name', None)
        if name is not None:
            names.append(name)
    if ('billing_expiration_month' in names
        and 'billing_expiration_year' in names
        and not 'billing_expiration' in names
        ):
        names.append('billing_expiration')
    return names


def update_field_errors(form, errors):
    """Update the form error elements based on the errors dict given.

    XXX: doctest
    """
    elements = CSSSelector('span[id$="-errors"]')(form)
    for e in elements:
        field_name = e.attrib['id'][:-7]          # Chop off '-errors'
        if field_name in errors:
            # Clear out the contents of the error element.
            for c in e.getchildren():
                e.remove(c)
            # Insert the error text into the error element.
            e.text = errors[field_name]
        else:
            # Remove the error element entirely when there is no error
            # for it.
            e.getparent().remove(e)
