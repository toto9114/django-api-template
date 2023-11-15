from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Union, Literal

from dataclasses_json import DataClassJsonMixin, config as ds_config

ALLOWED_EVENTS_TYPE = Literal[
    "insert", "update-tagging", "update-metadata", "tagging", "delete", "unknown"
]
ALLOWED_STATUS_TYPE = Literal["ok", "fail", "drop"]


@dataclass
class PipelineLogItem(DataClassJsonMixin):
    timestamp: Optional[datetime] = field(
        metadata=ds_config(
            encoder=lambda x: x.strftime("%Y-%m-%d %H:%M:%S.%f"),
            decoder=lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f"),
        ),
        default=None,
    )
    tracking_id: str = None
    request_id: str = None
    company_id: str = None
    pool_id: str = None
    product_id: str = None
    image_url: Optional[str] = None
    tagging_result_url: Optional[str] = None
    app_name: str = None
    event: Optional[ALLOWED_EVENTS_TYPE] = None
    status: Optional[ALLOWED_STATUS_TYPE] = None
    request_body: Optional[str] = None
    extra: Optional[Union[str, dict]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_detail: Optional[str] = None
    image_detection: Optional[str] = None
    sales_url: Optional[str] = None
    mobile_sales_url: Optional[str] = None
    name: Optional[str] = None
    currency: Optional[str] = None
    origin_price: Optional[float] = None
    discount_price: Optional[float] = None
    metadata: Optional[str] = None
    year: str = None
    month: str = None
    day: str = None
    hour: str = None

    def __post_init__(self):
        if self.timestamp is not None:
            self.year = str(self.timestamp.year)
            self.month = "{:02d}".format(self.timestamp.month)
            self.day = "{:02d}".format(self.timestamp.day)
            self.hour = "{:02d}".format(self.timestamp.hour)
