from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


@dataclass
class ModelMessageHeader(DataClassJsonMixin):
    id: str
    queue_url: str
    handle: str
    attributes: dict
    num_trial: int


@dataclass
class ModelMessage(DataClassJsonMixin):
    header: ModelMessageHeader
    body: str


@dataclass
class MessageSet(DataClassJsonMixin):
    header: ModelMessageHeader
    parsed: dict
