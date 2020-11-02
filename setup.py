from setuptools import setup

APP_NAME = 'discord-birthday-bot'

setup(
    name=APP_NAME,
    version='0.1.0.dev0',
    packages=['discord_birthday_bot'],
    url='https://github.com/SiKreuz/discord-birthday-bot',
    license='MIT',
    author='Simon Kreuzer',
    author_email='mail@monsi.org',
    description='A discord bot that saves your server\'s member\'s birthdays and does a friendly reminder on the '
                'birthday itself.',

    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'dc-birthday-bot=discord_birthday_bot.main:start'
        ]
    },
    package_data={'discord_birthday_bot': ['locale/**/*.mo']},
    setup_requires=['mo_installer'],
    locale_src='discord_birthday_bot/locale',
    locale_dir='discord_birthday_bot/locale',
    install_requires=[
        'discord~=1.0.1',
        'python-dotenv~=0.14.0',
        'setuptools~=50.3.2',
        'dateparser~=0.7.6',
        'click~=7.1.2',
        'psycopg2~=2.8.6',
        'appdirs~=1.4.4',
        'APScheduler~=3.6.3'
    ]
)
