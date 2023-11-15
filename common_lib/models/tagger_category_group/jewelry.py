from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from .common import TaggerPositionSchema, TaggerAttributeSchema
from typing import Optional


@dataclass
class TaggerJewelryTags(DataClassJsonMixin):
    category: Optional[TaggerAttributeSchema] = None
    position: Optional[TaggerPositionSchema] = None
    item: Optional[TaggerAttributeSchema] = None
    length: Optional[TaggerAttributeSchema] = None
    colors: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    details: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    mainMaterial: Optional[TaggerAttributeSchema] = None
    subMaterial: Optional[TaggerAttributeSchema] = None
