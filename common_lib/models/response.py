from dataclasses import dataclass
from typing import Optional, Any

from dataclasses_json import DataClassJsonMixin

from common_lib.dataclass.validate import DataclassValidations


@dataclass
class FlushBackendError(DataClassJsonMixin, DataclassValidations):
    code: str
    message: str


@dataclass
class FlushBackendBaseResponse(DataClassJsonMixin, DataclassValidations):
    data: Optional[Any]
    status: str
    error: Optional[FlushBackendError]


@dataclass
class FlushBackendErrorResponse(DataClassJsonMixin, DataclassValidations):
    error: FlushBackendError
    status: str = "fail"
    data: Optional[dict] = None
