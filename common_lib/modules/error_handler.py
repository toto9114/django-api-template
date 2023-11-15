from common_lib.error_codes.error_codes import ErrorStatus
from fastapi import HTTPException
from typing import Optional


class ManagedHttpException(HTTPException):
    def __init__(
        self,
        error_status: ErrorStatus,
        extra: Optional[dict] = None,
        exc_info: Optional[Exception] = None,
    ):
        if extra is None:
            extra = dict()
        self.extra = extra
        self.exc_info = exc_info if exc_info else self
        super().__init__(
            status_code=error_status.status_code,
            detail={
                "message": error_status.message,
                "code": error_status.code,
                **extra,
            },
        )
