from .command import Command
from ..storage import User, Cofi


class CofiCommand(Command):
    def __init__(self):
        self.cofi_commands = [
            '!cofi',
            '!cofe',
            '!coffi',
            '!coffe',
            '!coffee',
            '!coffeh',
            '!kofi',
            '!kofe',
            '!koffi',
            '!koffe',
            '!koffee'
            '!koffeh',
            '!kafi',
            '!kafe',
            '!kaffi',
            '!kaffe',
            '!kaffee',
            '!kaffeh',
            '!java',
            '!kafu',
            ':coffee:'
        ]

        self.cofi_stats_commands = [x + 'stats' for x in self.cofi_commands]

    def trigger(self, data):
        if 'text' not in data:
            return False

        text = data['text'].strip()
        return text in self.cofi_commands or text in self.cofi_stats_commands

    def handle(self, bot, data):
        text = data['text'].strip()

        if text in self.cofi_commands:
            self.handle_cofi(bot, data)
        elif text in self.cofi_stats_commands:
            self.handle_stats(bot, data)

    @staticmethod
    def handle_cofi(bot, data):
        user_id = data['user']
        user_name = bot.sc.server.users[data['user']].name

        with bot.database.session() as session:
            User.get_or_create(session, user_id, user_name)

        with bot.database.session() as session:
            user = User.get_or_create(session, user_id, user_name)
            Cofi.add(session, user)

        bot.react_with('coffee', data)

    @staticmethod
    def handle_stats(bot, data):
        user_id = data['user']
        user_name = bot.sc.server.users[data['user']].name
        real_name = bot.sc.server.users[data['user']].real_name

        if real_name:
            name = real_name
        else:
            name = user_name

        with bot.database.session() as session:
            User.get_or_create(session, user_id, user_name)

        with bot.database.session() as session:
            user = User.get_or_create(session, user_id, user_name)
            cofi_today = Cofi.get_today(session, user)
            cofi_total = Cofi.get_total(session, user)

        bot.send_message('%s has had %s cofi today! (Total: %s)' % (name, cofi_today, cofi_total), data)
