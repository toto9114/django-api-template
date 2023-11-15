from contextvars import ContextVar


class ContextWrapper:
    def __init__(self, value):
        self.__value: ContextVar = value

    def set(self, value):
        return self.__value.set(value)

    def reset(self, token):
        self.__value.reset(token)

    def __module__(self):
        return self.__value.get()

    @property
    def value(self):
        return self.__value.get()
