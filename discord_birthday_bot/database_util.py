import psycopg2

DATABASE = None
USERNAME = None
PASSWORD = None
HOST = None
PORT = None

TABLE_NAME_DATA = 'birthday'
COLUMN_PERSON_ID = 'person_id'
COLUMN_BIRTHDAY = 'birthday'
COLUMN_GUILD_ID = 'guild_id'
TABLE_NAME_SETTINGS = 'greeting_channel'
COLUMN_CHANNEL_ID = 'channel_id'
COLUMN_LIST_MSG_ID = 'list_msg_id'
COLUMN_lIST_MSG_CH_ID = 'list_msg_ch_id'


def connect():
    """Establishes the connection to the database."""
    try:
        return psycopg2.connect(
            user=USERNAME,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            database=DATABASE
        )
    except (Exception, psycopg2.Error) as error:
        print('Something went wrong:', error)
        return None


def disconnect(connection):
    """Closes the connection to the database."""
    if connection:
        connection.close()


def startup(name, user, password, host, port):
    """Saves the login credentials and creates the database table if not already existing.
    Returns True if database was set up successfully, False otherwise."""
    global DATABASE, USERNAME, PASSWORD, HOST, PORT
    DATABASE = name
    USERNAME = user
    PASSWORD = password
    HOST = host
    PORT = port

    connection = connect()
    if connection is not None:
        # Add new column on update from 0.1.x #
        query = f'ALTER TABLE IF EXISTS {TABLE_NAME_SETTINGS} ' \
                f'ADD COLUMN IF NOT EXISTS {COLUMN_LIST_MSG_ID} BIGINT, ' \
                f'ADD COLUMN IF NOT EXISTS {COLUMN_lIST_MSG_CH_ID} BIGINT; '

        # Create tables #
        query += f'CREATE TABLE IF NOT EXISTS {TABLE_NAME_DATA}' \
                 f'({COLUMN_PERSON_ID} BIGINT NOT NULL, ' \
                 f'{COLUMN_BIRTHDAY} DATE, ' \
                 f'{COLUMN_GUILD_ID} BIGINT, ' \
                 f'PRIMARY KEY ({COLUMN_PERSON_ID}, {COLUMN_GUILD_ID}));'
        query += f'CREATE TABLE IF NOT EXISTS {TABLE_NAME_SETTINGS}' \
                 f'({COLUMN_GUILD_ID} BIGINT PRIMARY KEY NOT NULL, ' \
                 f'{COLUMN_CHANNEL_ID} BIGINT, ' \
                 f'{COLUMN_LIST_MSG_ID} BIGINT, ' \
                 f'{COLUMN_lIST_MSG_CH_ID} BIGINT);'

        connection.cursor().execute(query)
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False


def insert(person):
    """Saves a person to the database. Returns True when successfully saved, False otherwise."""
    connection = connect()
    if connection is not None:
        query = f'INSERT INTO {TABLE_NAME_DATA} VALUES (%s, %s, %s) ' \
                f'ON CONFLICT ({COLUMN_PERSON_ID}, {COLUMN_GUILD_ID}) DO UPDATE ' \
                f'SET {COLUMN_BIRTHDAY} = %s;'
        connection.cursor().execute(query, (person.person_id, person.birthday, person.guild_id, person.birthday))
        connection.commit()
        disconnect(connection)
        print(f'Guild {person.guild_id}: '
              f'Added member {person.person_id} with birthday '
              + person.birthday.strftime('%x') + '.')
        return True
    else:
        return False


def delete(person):
    """Deletes a person and its birthday. Returns True when successfully saved, False otherwise."""
    connection = connect()
    if connection is not None:
        query = f'DELETE FROM {TABLE_NAME_DATA} ' \
                f'WHERE {COLUMN_PERSON_ID} = %s ' \
                f'AND {COLUMN_GUILD_ID} = %s;'
        cursor = connection.cursor()
        cursor.execute(query, (person.person_id, person.guild_id))
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False


def delete_all(guild_id):
    connection = connect()
    if connection is not None:
        query = f'DELETE FROM {TABLE_NAME_DATA} ' \
                f'WHERE {COLUMN_GUILD_ID} = %s;'
        cursor = connection.cursor()
        cursor.execute(query, (guild_id,))
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False


def get_birthday_children():
    """Getting all birthday children from the database and calculates their age."""
    connection = connect()
    if connection is not None:
        query = f'SELECT d.{COLUMN_PERSON_ID}, DATE_PART(\'year\', AGE({COLUMN_BIRTHDAY})), c.{COLUMN_CHANNEL_ID} ' \
                f'FROM {TABLE_NAME_DATA} AS d, {TABLE_NAME_SETTINGS} AS c ' \
                f'WHERE DATE_PART(\'month\', {COLUMN_BIRTHDAY}) = DATE_PART(\'month\', CURRENT_DATE) ' \
                f'AND DATE_PART(\'day\', {COLUMN_BIRTHDAY}) = DATE_PART(\'day\', CURRENT_DATE) ' \
                f'AND d.{COLUMN_GUILD_ID} = c.{COLUMN_GUILD_ID} ' \
                f'ORDER BY c.{COLUMN_CHANNEL_ID};'
        cursor = connection.cursor()
        cursor.execute(query)
        birthday_children = cursor.fetchall()
        disconnect(connection)
        return birthday_children
    else:
        return None


def list_all(guild_id):
    """Returns all birthday entries."""
    connection = connect()
    if connection is not None:
        query = f'SELECT {COLUMN_PERSON_ID}, {COLUMN_BIRTHDAY} ' \
                f'FROM {TABLE_NAME_DATA} ' \
                f'WHERE {COLUMN_GUILD_ID} = \'{guild_id}\' ' \
                f'ORDER BY TO_CHAR({COLUMN_BIRTHDAY}, \'MMDD\');'
        cursor = connection.cursor()
        cursor.execute(query)
        persons = cursor.fetchall()
        disconnect(connection)
        return persons
    else:
        return None


def get_list_msg_id(guild_id):
    """Saves the list message id."""
    connection = connect()
    if connection is not None:
        query = f'SELECT {COLUMN_lIST_MSG_CH_ID}, {COLUMN_LIST_MSG_ID} ' \
                f'FROM {TABLE_NAME_SETTINGS} ' \
                f'WHERE {COLUMN_GUILD_ID} = %s;'
        cursor = connection.cursor()
        cursor.execute(query, (guild_id,))
        msg_id = cursor.fetchall()
        disconnect(connection)
        return msg_id
    else:
        return None


def set_list_msg(guild_id, channel_id, msg_id):
    """Saves the list message id."""
    connection = connect()
    if connection is not None:
        query = f'INSERT INTO {TABLE_NAME_SETTINGS}({COLUMN_GUILD_ID}, {COLUMN_lIST_MSG_CH_ID}, {COLUMN_LIST_MSG_ID}) ' \
                f'VALUES (%s, %s, %s) ' \
                f'ON CONFLICT ({COLUMN_GUILD_ID}) DO UPDATE ' \
                f'SET {COLUMN_LIST_MSG_ID} = {msg_id}, ' \
                f'{COLUMN_lIST_MSG_CH_ID} = {channel_id};'
        connection.cursor().execute(query, (guild_id, channel_id, msg_id))
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False


def remove_list_msg(guild_id):
    """Removes the list message data from the given guild."""
    connection = connect()
    if connection is not None:
        query = f'UPDATE {TABLE_NAME_SETTINGS} ' \
                f'SET {COLUMN_LIST_MSG_ID} = NULL, ' \
                f'{COLUMN_lIST_MSG_CH_ID} = NULL;'
        connection.cursor().execute(query, (guild_id,))
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False


def set_channel(guild_id, channel_id):
    """Inserts an entry to the greeting_channel table."""
    connection = connect()
    if connection is not None:
        query = f'INSERT INTO {TABLE_NAME_SETTINGS} VALUES (%s, %s) ' \
                f'ON CONFLICT ({COLUMN_GUILD_ID}) DO UPDATE ' \
                f'SET {COLUMN_CHANNEL_ID} = {channel_id};'
        connection.cursor().execute(query, (guild_id, channel_id))
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False


def delete_guild(guild_id):
    """Deletes an guild in the greeting_channel table"""
    connection = connect()
    if connection is not None:
        query = f'DELETE FROM {TABLE_NAME_SETTINGS} ' \
                f'WHERE guild_id = {guild_id};'
        connection.cursor().execute(query)
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False
