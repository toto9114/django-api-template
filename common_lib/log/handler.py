from logging import handlers


class CustomSocketHandler(handlers.SocketHandler):
    def __init__(self, host, port, encoding="utf-8"):
        self.encoding = encoding
        super(CustomSocketHandler, self).__init__(host, port)

    def makePickle(self, record):
        return self.format(record).encode(self.encoding) + b"\n"
