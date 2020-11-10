import os

from pythongettext import msgfmt

LOCALE_PATH = os.path.join('..', 'discord_birthday_bot', 'locale')

for subdir, dirs, files in os.walk(LOCALE_PATH):
    for filename in files:
        if filename.endswith('.po'):
            path = os.path.join(subdir, filename)
            mo_str = msgfmt.Msgfmt(path).get()
            mo = open(os.path.splitext(path)[0] + '.mo', 'wb')
            mo.write(mo_str)
            mo.flush()
            mo.close()

            print('Translated', path)
