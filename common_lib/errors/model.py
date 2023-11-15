from dataclasses import dataclass
from http import HTTPStatus

from dataclasses_json import DataClassJsonMixin


@dataclass
class ManagedErrorModel(DataClassJsonMixin):
    code: int
    message: str
    http_status: int = HTTPStatus.BAD_REQUEST
