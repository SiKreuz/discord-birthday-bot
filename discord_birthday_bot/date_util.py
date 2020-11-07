import locale
from datetime import datetime

import dateparser
from babel.dates import format_date, get_date_format

from discord_birthday_bot import config_util as config

NO_YEAR = 1

STANDARD_LANG = 'en_US'

lang = config.get_language()

# Set locale #
try:
    locale.setlocale(locale.LC_ALL, lang + '.utf8')  # set locale
except locale.Error:
    print('Error: Locale %s not existing.' % lang)
    lang = STANDARD_LANG
    locale.setlocale(locale.LC_ALL, lang + '.utf8')


def get_current_locale():
    """Returns the current locale string without the '.utf8'."""
    return locale.getlocale(locale.LC_ALL)[0]


def parse_to_date(msg):
    """Parses a date string and returns a datetime object."""
    date = dateparser.parse(msg, locales=[get_current_locale()[:2]])  # parse date
    # If is current year, set year to 1 #
    if is_current_year(date):
        date = date.replace(year=NO_YEAR)
    return date


def parse_to_string(date):
    """Formats the date according to the current locale and the existence of the year."""
    date_format = get_date_format(format='long', locale=get_current_locale()).pattern
    if not has_year(date):
        date_format = date_format.replace('y', '').replace(',', '').rstrip()
    return format_date(date, format=date_format, locale=get_current_locale())


def has_year(date):
    """Returns True if the date contains the year, False otherwise."""
    return date.year != NO_YEAR


def is_current_year(date):
    """Returns True if the date is from the current year, False otherwise."""
    return date.year == datetime.now().year
