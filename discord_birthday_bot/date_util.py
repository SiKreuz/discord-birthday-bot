import locale

import dateparser

from discord_birthday_bot import config_util as config

lang = config.get_language()
if len(lang) == 2:
    lang += '_' + lang.upper()

LOCALE = lang + '.utf8'

# Set locale #
try:
    locale.setlocale(locale.LC_ALL, LOCALE)  # set locale
except locale.Error:
    print('Error: Locale %s not existing.' % LOCALE)
    LOCALE = 'en_US.utf8'
    locale.setlocale(locale.LC_ALL, LOCALE)


def parse_to_date(msg):
    """Parses a date string and returns a datetime object."""
    return dateparser.parse(msg, locales=[LOCALE[:2]])  # parse date


def parse_to_string(date):
    return date.strftime('%x')
