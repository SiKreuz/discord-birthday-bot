import configparser
import os
from pathlib import Path

import appdirs

APP_NAME = 'discord_birthday_bot'

CONFIG_DIR = appdirs.user_config_dir(APP_NAME)
CONFIG_FILE_NAME = 'config'
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)

BOT_SECTION = 'Bot'
BOT_TOKEN = ('token', '')
BOT_PREFIX = ('prefix', '!bd')
BOT_SPACE_AFTER_PREFIX = ('space_after_prefix', 'True')

DB_SECTION = 'PostgreSQL'
DB_NAME = ('name', 'postgres')
DB_USER = ('username', 'postgres')
DB_PASSWORD = ('password', '')
DB_HOST = ('host', '127.0.0.1')
DB_PORT = ('port', '5432')

LOC_SECTION = 'Locale'
LOC_LANGUAGE = ('language', 'en_US')

# create config directory if not already existing
if not Path(CONFIG_FILE_PATH).exists():
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)

# load existing config
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)


def init_section(section, options):
    """Creates all sections and options if not existing."""
    if not config.has_section(section):
        config.add_section(section)
    for option in options:
        if not config.has_option(section, option[0]):
            config.set(section, option[0], option[1])


init_section(BOT_SECTION, [BOT_TOKEN, BOT_PREFIX, BOT_SPACE_AFTER_PREFIX])
init_section(DB_SECTION, [DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT])
init_section(LOC_SECTION, [LOC_LANGUAGE])

with open(CONFIG_FILE_PATH, 'w+') as config_file:
    config.write(config_file)


def get_token():
    return config.get(BOT_SECTION, BOT_TOKEN[0])


def get_prefix():
    return config.get(BOT_SECTION, BOT_PREFIX[0])


def is_space_after_prefix():
    return config.getboolean(BOT_SECTION, BOT_SPACE_AFTER_PREFIX[0])


def get_db_name():
    return config.get(DB_SECTION, DB_NAME[0])


def get_db_user():
    return config.get(DB_SECTION, DB_USER[0])


def get_db_password():
    return config.get(DB_SECTION, DB_PASSWORD[0])


def get_db_host():
    return config.get(DB_SECTION, DB_HOST[0])


def get_db_port():
    return config.get(DB_SECTION, DB_PORT[0])


def get_language():
    l = config.get(LOC_SECTION, LOC_LANGUAGE[0])
    if l == '':
        l = 'en_US'
    return l
