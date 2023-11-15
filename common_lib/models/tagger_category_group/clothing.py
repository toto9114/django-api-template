from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from .common import TaggerPositionSchema, TaggerAttributeSchema
from typing import Optional


@dataclass
class TaggerClothingTags(DataClassJsonMixin):
    category: Optional[TaggerAttributeSchema] = None
    position: Optional[TaggerPositionSchema] = None
    item: Optional[TaggerAttributeSchema] = None
    length: Optional[TaggerAttributeSchema] = None
    sleeveLength: Optional[TaggerAttributeSchema] = None
    neckLine: Optional[TaggerAttributeSchema] = None
    fit: Optional[TaggerAttributeSchema] = None
    shape: Optional[TaggerAttributeSchema] = None
    colors: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    prints: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    textures: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    details: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
    looks: Optional[list[TaggerAttributeSchema]] = field(default_factory=list)
