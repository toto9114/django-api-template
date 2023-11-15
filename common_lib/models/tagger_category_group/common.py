from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin


# @dataclass
# class TaggerCategorySchema(DataClassJsonMixin):
#     id: str
#     name: str


@dataclass
class TaggerPositionSchema(DataClassJsonMixin):
    x: float
    y: float


@dataclass
class TaggerAttributeSchema(DataClassJsonMixin):
    id: str
    name: str
    confidence: float
