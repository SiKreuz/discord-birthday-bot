import click
import discord
from apscheduler.schedulers.background import BackgroundScheduler

import config_util as config
import database_util
import date_util
from output_util import e_print

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class Person:
    """Represents a member on the discord with its id and birthday."""

    def __init__(self, person_id, birthday):
        """Initializes a person with an id and its birthday."""
        self.person_id = person_id
        self.birthday = birthday


PREFIX = '!bdg'
GUILD = None

client = discord.Client()


@client.event
async def on_ready():
    """Confirms the connection to discord."""
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name} (id: {guild.id})')


@client.event
async def on_message(message):
    """Analyzes the incoming messages."""

    # Checks for the prefix and ignores all messages from itself #
    if not message.content.lower().startswith(PREFIX) or message.author == client.user:
        return

    msg = message.content[len(PREFIX) + 1:]  # msg without the prefix

    # Command list #
    if msg.startswith('list'):
        send_list(message.channel)
        return

    # Evaluate date given from the user #
    save_date(msg, message.channel, message.author)


def send_message(message, channel):
    """Sends a message into the given channel."""
    channel.send(message)


def send_list(channel):
    """Send the whole list of people and their birthdays into the given discord channel."""
    ret_msg = 'These are all birthdays I know:\n'
    for p in database_util.list_all():
        ret_msg += f'<@{p[0]}> - {p[1]}'
    send_message(ret_msg, channel)


def save_date(msg, channel, author):
    """Parses the date of the message and saves it to the database."""
    # Date handling #
    date = date_util.parse_date(msg)
    if date is None:
        send_message(f'Sry, but \'{msg}\' isn\'t a date.', channel)
        return

    # Insert into database #
    person = Person(author.id, date)
    database_util.insert(person)

    # Send return message #
    send_message(f'Save the date! <@{person.person_id}>\'s birthday is at the '
                 + person.birthday.strftime('%x')
                 + '.', channel)


def send_birthday_message():
    """Checks for the birthday children and sends a message."""
    birthday_children = database_util.get_birthday_children()
    msg = 'Today we have ' + str(len(birthday_children)) + ' birthday child(ren).\n'
    for child in birthday_children:
        msg += f'{child[0]} is now {child[1]} years old!\n'
    print(msg)
    # TODO the message has to be send to the discord chat


def start_scheduler():
    """Configures and starts the scheduler."""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(send_birthday_message, 'cron', day='*')
    scheduler.start()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', default=config.get_token(), help='Token of the bot account')
@click.option('--guild', '-g', default=config.get_guild(), help='Guild of the bot')
@click.option('--name', '-n', default=config.get_db_name(), help='Database name')
@click.option('--user', '-u', default=config.get_db_user(), help='Username to enter database')
@click.option('--password', '-s', default=config.get_db_password(), help='Password to enter database')
@click.option('--host', '-a', default=config.get_db_host(), help='URL of the database')
@click.option('--port', '-p', default=config.get_db_port(), help='Port of the database')
def start(token, guild, name, user, password, host, port):
    """Sets up the database, logs into discord and starts the cron job."""

    start_scheduler()

    global GUILD
    GUILD = guild
    if database_util.startup(name, user, password, host, port):
        try:
            client.run(token)
        except discord.errors.LoginFailure:
            e_print('Please check your login credentials at', config.CONFIG_FILE_PATH)
            exit(1)


if __name__ == '__main__':
    start()
