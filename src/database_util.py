import psycopg2

DATABASE = None
USERNAME = None
PASSWORD = None
HOST = None
PORT = None

TABLE_NAME_DATA = 'birthday'
TABLE_NAME_SETTINGS = 'settings'


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
        query = f'CREATE TABLE IF NOT EXISTS {TABLE_NAME_DATA}(id BIGINT PRIMARY KEY NOT NULL, birthday DATE);'
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
        query = f'INSERT INTO {TABLE_NAME_DATA} VALUES (%s, %s);'
        connection.cursor().execute(query, (person.person_id, person.birthday))
        connection.commit()
        disconnect(connection)
        print(f'Added member {person.person_id} with birthday ' + person.birthday.strftime('%x') + '.')
        return True
    else:
        return False


def list_all():
    """Returns all database entries."""
    connection = connect()
    if connection is not None:
        query = f'SELECT * FROM {TABLE_NAME_DATA};'
        cursor = connection.cursor()
        cursor.execute(query)
        persons = cursor.fetchall()
        disconnect(connection)
        return persons
    else:
        return None
