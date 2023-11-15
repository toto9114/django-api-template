from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Union, Optional

from dataclasses_json import DataClassJsonMixin


class EnumFeatureStatus(str, Enum):
    def __new__(cls, id: str):
        obj = str.__new__(cls, id)
        obj._value_ = id
        obj.id = id
        return obj

    NULL = None
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    ERROR = "ERROR"


class FeatureColorWeight(str, Enum):
    def __new__(cls, id: str):
        obj = str.__new__(cls, id)
        obj._value_ = id
        obj.id = id
        return obj

    LOW: str = "LOW"
    MEDIUM: str = "MEDIUM"
    HIGH: str = "HIGH"


@dataclass
class ModelFeatureInfo:
    feature_id: str = None
    pool_id: Optional[str] = None
    model_version: Optional[str] = None
    use_yn: Optional[bool] = False


@dataclass
class ModelFeatureList(DataClassJsonMixin):
    feature_id: str
    pool_id: str
    product_id: str
    rcmd_idx_grp: str = None
    srch_idx_grp: str = None
    detc_ctgr_grp: str = None
    feat_hash: Optional[str] = None
    s3_image_url: Optional[str] = None
    top: Optional[float] = None
    left: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    status: Union[str, None] = EnumFeatureStatus.NULL.value
    error: Optional[str] = None
    del_dt: Optional[datetime] = None


@dataclass
class FeatureListForGroup(DataClassJsonMixin):
    model_version: str
    feature_id: str
    product_id: str
    feat_hash: str
    rcmd_idx_grp: str = None
    srch_idx_grp: str = None
    detc_ctgr_grp: str = None


@dataclass
class ModelFeatureListForFailed(DataClassJsonMixin):
    feature_id: str
    product_id: str
    error: Optional[dict] = None


@dataclass
class ModelFeature(DataClassJsonMixin):
    feature_without_color: Union[list[float], None] = None
    feature_with_color: Union[list[float], None] = None
    feature_with_color_more: Union[list[float], None] = None


@dataclass
class SrcmdModelFeature(DataClassJsonMixin):
    feature: Union[list[float], None] = None


@dataclass
class FeatureForDelete(DataClassJsonMixin):
    feature_id: str
    product_id: str
    model_version: str


@dataclass
class FeatureHashWithObjectKey:
    __slots__ = ("feat_hash", "object_key")
    feat_hash: str
    object_key: str


@dataclass
class FeatureSet(DataClassJsonMixin):
    set_id: str
    feature_id: str
    model_version: str
    index_group_id: str
    feature_count: int = 0
    file_count: int = 0
    file_dir: str = None
    file_names: str = None
    day: Optional[int] = 1


@dataclass
class FeatureSetForDelete(DataClassJsonMixin):
    set_id: str
    feature_id: str
    file_count: int
    file_dir: str
    file_names: str
