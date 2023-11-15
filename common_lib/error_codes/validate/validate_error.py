from http import HTTPStatus

from common_lib.error_codes.error_codes import ErrorStatus


class ValidateErrorCommonStatus(ErrorStatus):
    WRONG_TYPE = ("VC001", "{}: '{}' instead of '{}'.", HTTPStatus.BAD_REQUEST)
