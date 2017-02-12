from .command import Command


def create_link(url, title):
    return '<%s|%s>' % (url, title)


class LunchCommand(Command):
    def __init__(self):
        self.commands = [
            '!lunch',
            '!mat',
            '!krubb',
            '!käk'
        ]

    def trigger(self, data):
        return 'text' in data and data['text'] in self.commands

    def handle(self, bot, data):
        overview = create_link('http://www.mjardevi.se/sv/guiden', 'Lunchguiden')
        matkultur = create_link('http://www.matkultur.net/', 'Matkultur')
        chililimi = create_link('http://chili-lime.se/', 'Chili-Lime')
        msg = '%s - %s - %s' % (overview, matkultur, chililimi)

        bot.web_send_message(msg, data)

