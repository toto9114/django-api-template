import signal


class GracefulKillHelper:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    @classmethod
    def exit_gracefully(cls, signum, frame):
        cls.kill_now = True
