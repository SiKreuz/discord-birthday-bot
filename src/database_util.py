import psycopg2

DATABASE = None
USERNAME = None
PASSWORD = None
HOST = None
PORT = None

TABLE_NAME = 'birthday'
COLUMN_ID = 'id'
COLUMN_BIRTHDAY = 'birthday'


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
        query = f'CREATE TABLE IF NOT EXISTS {TABLE_NAME}(' \
                f'{COLUMN_ID} BIGINT PRIMARY KEY NOT NULL, {COLUMN_BIRTHDAY} DATE' \
                f');'
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
        query = f'INSERT INTO {TABLE_NAME} ' \
                f'VALUES (%s, %s);'
        connection.cursor().execute(query, (person.person_id, person.birthday))
        connection.commit()
        disconnect(connection)
        print(f'Added member {person.person_id} with birthday ' + person.birthday.strftime('%x') + '.')
        return True
    else:
        return False


def get_birthday_children():
    """Getting all birthday children from the database and calculates their age."""
    connection = connect()
    if connection is not None:
        query = f'SELECT {COLUMN_ID}, DATE_PART(\'year\', AGE({COLUMN_BIRTHDAY})) ' \
                f'FROM {TABLE_NAME} ' \
                f'WHERE DATE_PART(\'month\', {COLUMN_BIRTHDAY}) = DATE_PART(\'month\', CURRENT_DATE) ' \
                f'AND DATE_PART(\'day\', {COLUMN_BIRTHDAY}) = DATE_PART(\'day\', CURRENT_DATE);'
        cursor = connection.cursor()
        cursor.execute(query)
        birthday_children = cursor.fetchall()
        disconnect(connection)
        return birthday_children
    else:
        return None


def list_all():
    """Returns all database entries."""
    connection = connect()
    if connection is not None:
        query = f'SELECT * FROM {TABLE_NAME};'
        cursor = connection.cursor()
        cursor.execute(query)
        persons = cursor.fetchall()
        disconnect(connection)
        return persons
    else:
        return None
