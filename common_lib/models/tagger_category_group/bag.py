from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from .common import TaggerPositionSchema, TaggerAttributeSchema
from typing import Optional


@dataclass
class TaggerBagTags(DataClassJsonMixin):
    category: Optional[TaggerAttributeSchema] = None
    position: Optional[TaggerPositionSchema] = None
    item: Optional[TaggerAttributeSchema] = None
    shape: Optional[TaggerAttributeSchema] = None
    strap: Optional[TaggerAttributeSchema] = None
    size: Optional[TaggerAttributeSchema] = None
    colors: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    prints: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    textures: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    details: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
