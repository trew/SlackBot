from .command import Command


def create_link(url, title):
    return '<%s|%s>' % (url, title)


class ResponseCommand(Command):
    def __init__(self):
        self.command_aliases = {
            '!pr': ['!pullrequest'],
            '!lunch': ['!mat', '!krubb', '!käk']
        }

        overview = create_link('http://www.mjardevi.se/sv/guiden', 'Lunchguiden')
        matkultur = create_link('http://www.matkultur.net/', 'Matkultur')
        chililimi = create_link('http://chili-lime.se/', 'Chili-Lime')
        lunch_response = '%s - %s - %s' % (overview, matkultur, chililimi)

        self.responses = {
            '!pr': ['Make a pull request! https://github.com/trew/SlackBot', True],
            '!lunch': [lunch_response, True]
        }

        self.aliases = {}
        for command, aliases in self.command_aliases.items():
            for alias in aliases:
                self.aliases[alias] = command

    def trigger(self, data):
        if 'text' not in data:
            return False

        text = data['text'].strip()

        return text in self.responses.keys() or text in self.aliases.keys()

    def handle(self, bot, data):
        text = data['text'].strip()
        if text in self.responses:
            command = self.responses[text]
        elif text in self.aliases:
            command = self.responses[self.aliases[text]]
        else:
            raise RuntimeError("Something went wrong")

        if command[1]:
            bot.web_send_message(command[0], data)
        else:
            bot.send_message(command[0], data)
