import click
import discord
from apscheduler.schedulers.background import BackgroundScheduler
from discord.ext import commands

import config_util as config
import database_util
import date_util
from output_util import e_print

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


class Person:
    """Represents a member on the discord with its id and birthday."""

    def __init__(self, person_id, birthday, guild_id):
        """Initializes a person with an id and its birthday."""
        self.person_id = person_id
        self.birthday = birthday
        self.guild_id = guild_id


PREFIX = '!bdg '
bot = commands.Bot(command_prefix=PREFIX)


@bot.event
async def on_ready():
    """Confirms the connection to discord."""
    print('%s is connected to discord.' % bot.user)


@bot.command(name='set')
async def save_date(ctx, date):
    """Saves the birthday of the user."""
    # Date handling #
    parsed_date = date_util.parse_to_date(date)
    if parsed_date is None:
        raise commands.BadArgument(date)

    # Insert into database #
    person = Person(ctx.author.id, parsed_date, ctx.guild.id)
    database_util.insert(person)

    # Send return message #
    bot.loop.create_task(send_message(f'Save the date! <@{person.person_id}>\'s birthday is at the '
                                      + date_util.parse_to_string(person.birthday)
                                      + '.', ctx.channel))


@bot.command(name='list')
@commands.has_permissions(administrator=True)
async def list_birthdays(ctx):
    """Prints a list of all saved birthdays."""
    ret_msg = 'These are all birthdays I know:\n'
    for p in database_util.list_all(ctx.guild.id):
        ret_msg += f'{date_util.parse_to_string(p[1])} - <@{p[0]}>\n'
    bot.loop.create_task(send_message(ret_msg, ctx.channel))


@bot.command(name='set-channel')
@commands.has_permissions(administrator=True)
async def set_channel(ctx):
    """Sets current channel for upcoming congratulations."""
    database_util.set_channel(ctx.guild.id, ctx.channel.id)
    ret_msg = 'Alright. All birthday greetings will be posted in this channel now.'
    bot.loop.create_task(send_message(ret_msg, ctx.channel))


@save_date.error
@list_birthdays.error
@set_channel.error
async def set_channel_error(ctx, error):
    """Handles all errors of incoming commands."""
    if isinstance(error, commands.MissingPermissions):
        ret_msg = 'Sorry, but you don\'t have the necessary permissions to use this command.'
    elif isinstance(error, commands.BadArgument):
        ret_msg = 'Sry, but \'%s\' isn\'t a date.' % error.args[0]
    else:
        ret_msg = 'Sorry, but something went wrong. Please advise the administrator.'
    bot.loop.create_task(send_message(ret_msg, ctx.channel))


async def send_message(message, channel):
    """Sends a message into the given channel."""
    await channel.send(message)


def send_birthday_message():
    """Checks for the birthday children and sends a message."""
    birthday_children = database_util.get_birthday_children()
    for child in birthday_children:
        channel = bot.get_channel(child[2])
        bot.loop.create_task(send_message(f'<@{child[0]}> is now {int(child[1])} years old!', channel))


def start_scheduler():
    """Configures and starts the scheduler."""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(send_birthday_message, 'cron', day='*')
    scheduler.start()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', default=config.get_token(), help='Token of the bot account')
@click.option('--name', '-n', default=config.get_db_name(), help='Database name')
@click.option('--user', '-u', default=config.get_db_user(), help='Username to enter database')
@click.option('--password', '-s', default=config.get_db_password(), help='Password to enter database')
@click.option('--host', '-a', default=config.get_db_host(), help='URL of the database')
@click.option('--port', '-p', default=config.get_db_port(), help='Port of the database')
def start(token, name, user, password, host, port):
    """Sets up the database, logs into discord and starts the cron job."""

    start_scheduler()

    if database_util.startup(name, user, password, host, port):
        try:
            bot.run(token)
        except discord.errors.LoginFailure:
            e_print('Please check your login credentials at', config.CONFIG_FILE_PATH)
            exit(1)


if __name__ == '__main__':
    start()
