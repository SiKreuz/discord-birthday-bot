import locale

import dateparser


def parse_date(msg):
    """Parses a date string and returns a datetime object."""
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')  # set locale
    return dateparser.parse(msg)  # parse date
