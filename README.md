# Discord Birthday Bot

This a small bot for discord servers to collect birthdays of the members and congratulate on the corresponding day.
Every member has to set its birthday on its own.
The bot will congratulate at midnight.

## Installation

Prerequisites: Python 3 and pip installed on your computer.
The following command installs all dependencies and the bot on your computer.
```shell script
pip install git+https://github.com/SiKreuz/discord-birthday-bot.git
```

If you like to install the bot system-wide, you need superuser-rights, off course.

### Create a Discord application / bot

Before you can use this bot, you have to create an application on Discord, which can be done [here](https://discord.com/developers/applications).
Follow [these instructions](https://discordpy.readthedocs.io/en/latest/discord.html) to properly create a bot.
You only have to tick the permissions *View Channels* and *Send Messages*.

### Setup PostgreSQL database

In order to save all birthdays the bot needs an existing [PostgreSQL](https://www.postgresql.org) database.
So download and setup PostgreSQL on your desired device and create a database.
You can also access the database from remote if you want to.

## Usage

### Start the bot

```
Usage: dc-birthday-bot [OPTIONS]

  Log into discord and listens for any command on all channels on all
  servers the bot was added to.

Options:
  -t, --token TEXT     Token of the bot account
  -n, --name TEXT      Database name
  -u, --user TEXT      Username to enter database
  -s, --password TEXT  Password to enter database
  -a, --host TEXT      URL of the database
  -p, --port TEXT      Port of the database
  -l, --language TEXT  Language in which the bot shall talk
  -h, --help           Show this message and exit.
```

You can pass all credentials (for Discord and PostgreSQL) via command line or save them in the configuration file.
It can be found in the for the system typical location, which would be `~/.config/discord_birthday_bot/config` on Linux.

#### Supported languages

You can set the language in which the bot shall talk to the server members.
Furthermore, the format in which the birthdays will be read is changed.

- English (US) - `MM/DD/YYYY`
- Deutsch (German) - `DD.MM.YYYY`

## Commands on Discord

[//]: <> (TODO update according to eventually new prefix handling)

The prefix for the bot is `!bdg`, so every of the following commands needs this prefix in front of it (e.g. `!bdg set 01/01/2000`).
```
Admin:
  delete-all  Deletes all saved birthdays.
  list        Prints a list of all saved birthdays.
  set-channel Sets current channel for upcoming congratulations.
Everyone:
  delete      Deletes the user's birthday.
  set         Saves the birthday of the user.
No Category:
  help        Shows this message

Type !bdg help command for more info on a command.
You can also type !bdg help category for more info on a category.
```
