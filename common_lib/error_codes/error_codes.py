from enum import Enum
from http import HTTPStatus


class ErrorStatus(str, Enum):
    def __new__(cls, code: str, message: str, status_code: HTTPStatus):
        obj = str.__new__(cls, code)
        obj._value_ = code

        obj.code = code
        obj.message = message
        obj.status_code = status_code
        return obj
