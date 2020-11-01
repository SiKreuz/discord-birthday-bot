import locale

import dateparser

LOCALE = 'en_US.utf8'
locale.setlocale(locale.LC_ALL, LOCALE)  # set locale


def parse_to_date(msg):
    """Parses a date string and returns a datetime object."""
    return dateparser.parse(msg)  # parse date


def parse_to_string(date):
    return date.strftime('%x')
