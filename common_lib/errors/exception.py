from dataclasses import dataclass, asdict
from http import HTTPStatus
from typing import Union, Optional

from common_lib.error_codes.error_codes import ErrorStatus


@dataclass
class ExtraModel:
    company_id: Optional[str] = None
    pool_id: Optional[str] = None
    product_id: Optional[str] = None
    request_id: Optional[str] = None
    tracking_id: Optional[str] = None
    traceback: Optional[str] = None
    etc: Optional[dict] = None

    def __post_init__(self):
        if self.etc is not None:
            [setattr(self, k, v) for k, v in self.etc.items()]


class ErrorWithExtraInfo(Exception):
    def __init__(
        self, message: str, extra: Union[ExtraModel, dict] = None, exc_info: any = None
    ):
        """
        Log에 추가 정보를 포함하기 위한 Exception Object
        Args:
            message: Error Message
            extra: dict type, log에 포함할 정보
            exc_info: Exception (원래의 exception 정보가 있는 경우) Exception Object
        """
        Exception.__init__(self, message)
        self.message: str = message
        if isinstance(extra, ExtraModel):
            self.extra: dict = asdict(extra)
        elif isinstance(extra, dict):
            self.extra: dict = extra
        else:
            self.extra: dict = {}
        self.exc_info = exc_info if exc_info is not None else self


class ManagedErrorWithExtraInfo(ErrorWithExtraInfo):
    def __init__(
        self,
        error_info: ErrorStatus,
        extra: Optional[ExtraModel] = None,
        exc_info: Optional[any] = None,
    ):
        self.error_info = error_info
        ErrorWithExtraInfo.__init__(
            self, message=error_info.message, extra=extra, exc_info=exc_info
        )


class BaseHTTPError(ErrorWithExtraInfo):
    def __init__(
        self,
        code: str = "1000",
        http_status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        message: str = "",
        status: str = "fail",
        data: Union[dict, None] = None,
        extra: Union[dict, None] = None,
        exc_info: any = None,
    ):
        """
        :param code: Customized ERROR Code
        :param http_status_code: HTTP Status Code
        :param message: Customized message
        :param status: Status string in Response body
        :param data: Data in Response Body
        :param extra: Extra info to ingest log data
        :param exc_info: Exception in original if exists
        """
        ErrorWithExtraInfo.__init__(
            self,
            message=message,
            extra=extra,
            exc_info=exc_info if exc_info is not None else self,
        )
        self.code = code
        self.http_status_code = http_status_code
        self.message = message
        self.status = status
        self.data = {} if data is None else data

    def to_response_dict(self):
        return {
            "data": self.data,
            "error": {"code": self.code, "message": self.message},
            "status": self.status,
        }
