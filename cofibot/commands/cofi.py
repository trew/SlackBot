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

    def trigger(self, data):
        return 'text' in data and data['text'] in self.cofi_commands

    def handle(self, bot, data):
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
            Cofi.add(session, user)
            cofi_today = Cofi.get_today(session, user)
            cofi_total = Cofi.get_total(session, user)

        bot.send_message('%s has had %s cofi today! (Total: %s)' % (name, cofi_today, cofi_total), data)
