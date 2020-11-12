import gettext
import os
from asyncio import TimeoutError

import click
import discord
from apscheduler.schedulers.background import BackgroundScheduler
from discord.ext import commands

from discord_birthday_bot import config_util as config
from discord_birthday_bot import database_util
from discord_birthday_bot import date_util
from discord_birthday_bot.output_util import e_print

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')
_ = gettext.gettext

PREFIX = '!bdg '
bot = commands.Bot(command_prefix=PREFIX)


class Person:
    """Represents a member on the discord with its id and birthday."""

    def __init__(self, person_id, birthday, guild_id):
        """Initializes a person with an id and its birthday."""
        self.person_id = person_id
        self.birthday = birthday
        self.guild_id = guild_id


class Everyone(commands.Cog):
    @commands.command(name='set')
    async def save_date(self, ctx, date):
        """Saves the birthday of the user."""
        # Date handling #
        parsed_date = date_util.parse_to_date(date)
        if parsed_date is None:
            raise commands.BadArgument(date)

        # Insert into database #
        person = Person(ctx.author.id, parsed_date, ctx.guild.id)
        database_util.insert(person)

        # Send return message #
        date = date_util.parse_to_string(person.birthday)
        await send_message(_('Save the date! <@%s>\'s birthday is at the %s.')
                           % (person.person_id, date),
                           ctx.channel)
        await update_list_message(ctx)  # Update birthday list

    @commands.command(name='delete')
    async def delete_date(self, ctx):
        """Deletes the user's birthday."""
        person = Person(ctx.author.id, None, ctx.guild.id)
        if database_util.delete(person):
            await send_message(_('<@%s>, I have forgotten your birthday. Do you even have one?')
                               % person.person_id,
                               ctx.channel)
            await update_list_message(ctx)  # Update birthday list


class Admin(commands.Cog):
    @commands.command(name='list')
    @commands.has_permissions(administrator=True)
    async def list_birthdays(self, ctx):
        """Prints a list of all saved birthdays.

        The list will be updated on each change. So a new birthday or deletion will update this message.
        """
        # Write new message #
        ret_msg = get_birthday_list(ctx.guild)
        msg = await send_message(ret_msg, ctx.channel)

        # Delete old message #
        old_msg = await get_list_msg(ctx.guild)
        if old_msg is not None:
            await old_msg.delete()

        # Update database
        database_util.set_list_msg(ctx.guild.id, ctx.channel.id, msg.id)

    @commands.command(name='set-channel')
    @commands.has_permissions(administrator=True)
    async def set_channel(self, ctx):
        """Sets current channel for upcoming congratulations."""
        database_util.set_channel(ctx.guild.id, ctx.channel.id)
        ret_msg = _('Alright. All birthday greetings will be posted in this channel now.')
        await send_message(ret_msg, ctx.channel)

    @commands.command(name='delete-all')
    @commands.has_permissions(administrator=True)
    async def delete_all(self, ctx):
        """Deletes all saved birthdays."""
        # Sends confirmation message and reacts with thumb up #
        msg = await send_message(_('Do you really want to delete all birthdays? This cannot be undone!'), ctx.channel)
        await msg.add_reaction('👍')

        # Wait for reaction and delete all birthdays afterwards. #
        try:
            if await bot.wait_for('reaction_add',
                                  timeout=30.0,
                                  check=lambda reaction, user: user == ctx.author and reaction.emoji == '👍'):
                database_util.delete_all(ctx.guild.id)
                await send_message(_('I have forgotten all your birthdays. Tell me some!'), ctx.channel)
                await update_list_message(ctx)  # Update birthday list
        except TimeoutError:
            await send_message(_('You didn\'t react in-time. I\'ll just forget about that.'), ctx.channel)


@bot.event
async def on_command_error(ctx, error):
    """Handles all errors of incoming commands."""
    if isinstance(error, commands.CommandNotFound):
        ret_msg = _('Sorry, but this command does not exist. With `!bdg help` you can list all available commands.')
    elif isinstance(error, commands.MissingPermissions):
        ret_msg = _('Sorry, but you don\'t have the necessary permissions to use this command.')
    elif isinstance(error, commands.BadArgument):
        ret_msg = _('Sry, but \'%s\' isn\'t a date.' % error.args[0])
    else:
        print(error)
        ret_msg = _('Sorry, but something went wrong. Please advise the administrator.')
    bot.loop.create_task(send_message(ret_msg, ctx.channel))


@bot.event
async def on_guild_remove(guild):
    """Deletes guild if bot leaves it"""
    database_util.delete_guild(guild_id=guild.id)
    print('The bot left %s' % guild.name)


@bot.event
async def on_member_remove(person):
    """Deletes person if it leaves guild"""
    database_util.delete(person)


async def get_list_msg(guild):
    """Returns the list message."""
    res = database_util.get_list_msg_id(guild.id)

    # Skip if nothing found #
    if not res:
        return None

    ch_id = res[0][0]
    msg_id = res[0][1]

    # Skip if no channel or message is defined #
    if ch_id is None or msg_id is None:
        return None

    try:
        ch = bot.get_channel(ch_id)
        msg = await ch.fetch_message(msg_id)
        return msg
    except (discord.NotFound, AttributeError):
        # Remove list message data from database #
        database_util.remove_list_msg(guild.id)
        return None


async def update_list_message(ctx):
    """Updates the list message with the current data from the database."""
    msg = await get_list_msg(ctx.guild)
    if msg is not None:
        await msg.edit(content=get_birthday_list(ctx.guild))


async def send_message(message, channel):
    """Sends a message into the given channel."""
    return await channel.send(message)


def get_birthday_list(guild):
    """Returns a list of all birthdays as string for posting at the discord server."""
    birthday_list = database_util.list_all(guild.id)
    if not birthday_list:
        msg = _('I don\'t know any birthdays. Tell me some!')
    else:
        msg = _('These are all birthdays I know:') + '\n' + '\n'.join(
            map(lambda m: '%s - <@%s>' % (date_util.parse_to_string(m[1]), m[0]), birthday_list))
    return msg


def send_birthday_message():
    """Checks for the birthday children and sends a message."""
    birthday_children = database_util.get_birthday_children()
    for child in birthday_children:
        channel = bot.get_channel(child[2])

        # Ping everyone if permission is granted #
        if channel.guild.me.permissions_in(channel).mention_everyone:
            msg = '@everyone '
        else:
            msg = ''

        # Create message depending if the birthday contains a year #
        if child[1] < 2000:
            msg += _('Let\'s party! <@%s> is now %s years old!') % (child[0], int(child[1]))
        else:
            msg += _('Let\'s party! It\'s <@%s> birthday today!') % (child[0])

        bot.loop.create_task(send_message(msg, channel))


def start_scheduler():
    """Configures and starts the scheduler."""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(send_birthday_message, 'cron', day='*')
    scheduler.start()


def set_language(lang):
    global _
    trans = gettext.translation('main', localedir=LOCALE_DIR, languages=[lang], fallback=True)
    trans.install()
    _ = trans.gettext


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option('--token', '-t', default=config.get_token(), help='Token of the bot account')
@click.option('--name', '-n', default=config.get_db_name(), help='Database name')
@click.option('--user', '-u', default=config.get_db_user(), help='Username to enter database')
@click.option('--password', '-s', default=config.get_db_password(), help='Password to enter database')
@click.option('--host', '-a', default=config.get_db_host(), help='URL of the database')
@click.option('--port', '-p', default=config.get_db_port(), help='Port of the database')
@click.option('--language', '-l', default=config.get_language(), help='Language in which the bot shall talk')
def start(token, name, user, password, host, port, language):
    """Log into discord and listens for any command on all channels on all servers the bot was added to."""

    set_language(language)

    bot.add_cog(Everyone())
    bot.add_cog(Admin())

    if database_util.startup(name, user, password, host, port):
        try:
            start_scheduler()
            bot.run(token)
        except discord.errors.LoginFailure:
            e_print('Please check your login credentials at', config.CONFIG_FILE_PATH)
            exit(1)


if __name__ == '__main__':
    start()
