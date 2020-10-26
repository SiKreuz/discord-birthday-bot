import configparser
from pathlib import Path

import appdirs

APP_NAME = 'discordBirthdayBot'

CONFIG_DIR = appdirs.user_config_dir(APP_NAME)
CONFIG_FILE_NAME = 'config'
CONFIG_FILE_PATH = CONFIG_DIR + '/' + CONFIG_FILE_NAME

BOT_SECTION = 'Bot'
TOKEN = 'token'

DB_SECTION = 'PostgreSQL'
DB_NAME = 'name'
DB_USER = 'username'
DB_PASSWORD = 'password'
DB_HOST = 'host'
DB_PORT = 'port'

# create config directory if not already existing
if not Path(CONFIG_FILE_PATH).exists():
    Path(CONFIG_DIR).mkdir(parents=True, exist_ok=True)

# load existing config
config = configparser.ConfigParser()
config.read(CONFIG_FILE_PATH)

# add sections if not existing
if not config.has_section(BOT_SECTION):
    config.add_section(BOT_SECTION)
    config.set(BOT_SECTION, TOKEN, '')
if not config.has_section(DB_SECTION):
    config.add_section(DB_SECTION)
    config.set(DB_SECTION, DB_NAME, 'postgres')
    config.set(DB_SECTION, DB_USER, 'postgres')
    config.set(DB_SECTION, DB_PASSWORD, '')
    config.set(DB_SECTION, DB_HOST, '127.0.0.1')
    config.set(DB_SECTION, DB_PORT, '5432')

with open(CONFIG_FILE_PATH, 'w+') as config_file:
    config.write(config_file)


def get_token():
    return config.get(BOT_SECTION, TOKEN)


def get_db_name():
    return config.get(DB_SECTION, DB_NAME)


def get_db_user():
    return config.get(DB_SECTION, DB_USER)


def get_db_password():
    return config.get(DB_SECTION, DB_PASSWORD)


def get_db_host():
    return config.get(DB_SECTION, DB_HOST)


def get_db_port():
    return config.get(DB_SECTION, DB_PORT)
