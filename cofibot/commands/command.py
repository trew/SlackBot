class Command(object):
    def trigger(self, data):
        raise NotImplementedError()

    def handle(self, bot, data):
        raise NotImplementedError()
