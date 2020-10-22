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
TABLE_NAME_SETTINGS = 'settings'
COLUMN_CHANNEL_ID = 'channel_id'


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
        connection.cursor().close()
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
        query = f'CREATE TABLE IF NOT EXISTS {TABLE_NAME_DATA}' \
                f'({COLUMN_PERSON_ID} BIGINT PRIMARY KEY NOT NULL,' \
                f'{COLUMN_BIRTHDAY} DATE,' \
                f'{COLUMN_GUILD_ID} BIGINT); ' \
                f'CREATE TABLE IF NOT EXISTS {TABLE_NAME_SETTINGS}' \
                f'({COLUMN_GUILD_ID} BIGINT PRIMARY KEY NOT NULL, {COLUMN_CHANNEL_ID} BIGINT);'
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
        query = f'INSERT INTO {TABLE_NAME_DATA} VALUES (%s, %s, %s);'
        connection.cursor().execute(query, (person.person_id, person.birthday, person.guild_id))
        connection.commit()
        disconnect(connection)
        print(f'Guild {person.guild_id}: '
              f'Added member {person.person_id} with birthday '
              + person.birthday.strftime('%x') + '.')
        return True
    else:
        return False


def list_all(guild_id):
    """Returns all database entries."""
    connection = connect()
    if connection is not None:
        query = f'SELECT {COLUMN_PERSON_ID}, {COLUMN_BIRTHDAY} ' \
                f'FROM {TABLE_NAME_DATA} ' \
                f'WHERE {COLUMN_GUILD_ID} = \'{guild_id}\';'
        cursor = connection.cursor()
        cursor.execute(query)
        persons = cursor.fetchall()
        disconnect(connection)
        return persons
    else:
        return None


def set_channel(guild_id, channel_id):
    connection = connect()
    if connection is not None:
        query = f'INSERT INTO {TABLE_NAME_SETTINGS} VALUES (%s, %s)'
        connection.cursor().execute(query, (guild_id, channel_id))
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False
