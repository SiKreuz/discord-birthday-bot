import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv('POSTGRESQL_USER')
PASSWORD = os.getenv('POSTGRESQL_PASSWORD')
DATABASE = os.getenv('POSTGRESQL_DATABASE')
HOST = os.getenv('POSTGRESQL_HOST')
PORT = os.getenv('POSTGRESQL_PORT')

TABLE_NAME = 'birthday'


def connect():
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
    if connection:
        connection.cursor().close()
        connection.close()


def startup():
    connection = connect()
    if connection is not None:
        query = f'CREATE TABLE IF NOT EXISTS {TABLE_NAME}(id BIGINT PRIMARY KEY NOT NULL, birthday DATE);'
        connection.cursor().execute(query)
        connection.commit()
        disconnect(connection)
        return True
    else:
        return False


def insert(person):
    connection = connect()
    if connection is not None:
        query = f'INSERT INTO {TABLE_NAME} VALUES (%s, %s);'
        connection.cursor().execute(query, (person.person_id, person.birthday))
        connection.commit()
        disconnect(connection)
        print(f'Added member {person.person_id} with birthday ' + person.birthday.strftime('%x') + '.')
        return True
    else:
        return False


def list_all():
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
