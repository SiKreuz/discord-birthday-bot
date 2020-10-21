import locale
import os

import dateparser
import discord
from dotenv import load_dotenv

import database_util


class Person:
    def __init__(self, person_id, birthday):
        self.person_id = person_id
        self.birthday = birthday


PREFIX = '!bdg'

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name} (id: {guild.id})')


@client.event
async def on_message(message):
    # Checks for the prefix and ignores all messages from itself #
    if not message.content.lower().startswith(PREFIX) or message.author == client.user:
        return

    if message.content[len(PREFIX):].startswith(' list'):
        msg = 'These are all birthdays I know:\n'
        for p in database_util.list_all():
            msg += f'<@{p[0]}>: {p[1]}'

        await message.channel.send(msg)
        return

    # Check for date #
    locale.setlocale(locale.LC_ALL, 'en_US.utf8')  # set locale
    date = dateparser.parse(message.content[len(PREFIX):])  # parse date
    if date is None:
        await message.channel.send(f'Sry, but \'{message.content[len(PREFIX):]}\' isn\'t a date.')
        return

    # Insert into database #
    person = Person(message.author.id, date)
    database_util.insert(person)

    # Send return message #
    await message.channel.send(f'Save the date! <@{person.person_id}>\'s birthday is at the '
                               + person.birthday.strftime('%x')
                               + '.')


def start():
    if database_util.startup():
        client.run(TOKEN)


if __name__ == '__main__':
    start()
