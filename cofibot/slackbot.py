import logging
import time
from threading import Thread

from slackclient import SlackClient
from websocket import WebSocketConnectionClosedException

from .commands import CofiCommand, ResponseCommand
from .storage import Database

log = logging.getLogger(__name__)


class SlackBot(object):
    def __init__(self, config: dict):
        self.sc = SlackClient(config['token'])
        self.database = Database(config['database'])
        self.commands = [
            CofiCommand(),
            ResponseCommand()
        ]

    def start(self):
        self.sc.rtm_connect()
        log.info("Connected")

        log.debug("Channels:")
        for channel in self.sc.server.channels:
            log.debug("ID: %s Name: %s", channel.id, channel.name)

        log.debug("Users:")
        for user_id, user in self.sc.server.users.items():
            log.debug("ID: %s Name: %s", user_id, user.name)

        slack_thread = Thread(name="CofiBot", target=slack_listener, args=(self,))
        slack_thread.start()
        log.info("Thread started")

    def handle(self, data: list):
        log.debug(data)
        for elem in data:
            if elem.get('type') == 'message' and not is_private_message(elem):
                for command in self.commands:
                    if command.trigger(elem):
                        command.handle(self, elem)

    def send_message(self, message, data):
        self.sc.rtm_send_message(data['channel'], message)

    def web_send_message(self, message, data):
        """
        If you want to format links, then this is the method to call
        """
        channel = self.sc.server.channels.find(data['channel'])
        self.sc.api_call('chat.postMessage', channel=channel.id, text=message, username=self.sc.server.username)

    def react_with(self, reaction, data):
        """
        Reacts to a message. Finding a message is simply a combination of channel ID and timestamp.
        """
        channel = self.sc.server.channels.find(data['channel'])
        timestamp = data['ts']
        self.sc.api_call('reactions.add', name=reaction, channel=channel.id, timestamp=timestamp)


def is_private_message(data):
    return data['channel'].startswith('D')


def slack_listener(bot: SlackBot):
    while True:
        try:
            data = bot.sc.rtm_read()
        except (WebSocketConnectionClosedException, ConnectionResetError) as e:
            log.exception(e)
            log.info("Attempting reconnect...")
            bot.sc.rtm_connect()
            continue

        if data:
            bot.handle(data)
        time.sleep(1)
