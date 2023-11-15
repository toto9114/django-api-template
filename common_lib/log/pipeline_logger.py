from datetime import datetime
from typing import Optional

import ujson as json

from common_lib.errors import ErrorWithExtraInfo
from common_lib.errors.exception import ExtraModel
from common_lib.infra.sqs_bulk import SQSClient
from common_lib.models.pipeline_logger import PipelineLogItem
from common_lib.utils.singleton import Singleton, initialize_once

# update-tagging : tagging 정보 변경 될 때 / detection, image-url 등 변경
# update-metadata : 그 이외가 변경될때
ALLOWED_EVENTS = [
    "insert",
    "tagging",
    "update-tagging",
    "update-metadata",
    "delete",
    "unknown",
]
ALLOWED_STATUS = ["ok", "fail", "drop"]


class PipelineLoggerValidationError(ErrorWithExtraInfo):
    """Data Validation Error"""


class PipelineLoggerRuntimeError(ErrorWithExtraInfo):
    """Runtime Error"""


class PipelineLogger(Singleton):
    @initialize_once
    def __init__(self, name: str = "default"):
        self.name = name
        self.app_name = None
        self.pipeline_log_queue = None
        self.sqs = None

    def initialize(
        self,
        app_name: str,
        pipeline_log_queue: str,
    ):
        self.app_name = app_name
        self.sqs = SQSClient(
            sqs_name=pipeline_log_queue,
        )

    def put(
        self,
        data: list[PipelineLogItem],
        logger=None,
        event: Optional[str] = None,
        status: Optional[str] = None,
    ):
        """
        DataLake에 로그를 기록합니다. Exception 발생하는 경우 모든 data가 들어가지 않으니 로직상 검토가 필요합니다.
        Erro 종류:
         + PipelineLoggerValidationError: 입력 data가 아래 조건을 충족하지 않는 경우 발생.
                                          이 경우 모든 data는 입력되지 않습니다!
         + PipelineLoggerRuntimeError: AWS Firehose API 호출 중 오류가 발생하는 경우.
                                          이 경우 모든 data는 입력되지 않을 가능성이 높습니다.

        **중요** event, status 필드 값은 put() 함수 인자 또는 data 중 어느 한 곳에는 반드시 존재해야 합니다.
        @param data: list[PipelineLogItem] 형태의 데이터
        @param event: (optional) 값이 있는 경우 입력 항목의 모든 event 값을 해당 값으로 대체합니다.
                              소문자로 ["insert", "update-tagging","update-metadata", "unknown"] 만 입력 가능합니다.
        @param status: (optional) 값이 있는 경우 입력 항목의 모든 status 값을 해당 값으로 대체합니다.
                              소문자로 ["ok", "fail", "drop"] 만 입력 가능합니다.
        @return:
        """
        now = datetime.utcnow()
        records: list[str] = [
            json.dumps(
                self._convert_item(item, now, event, status).to_dict(),
                ensure_ascii=False,
            )
            for item in data
        ]
        self.sqs.publish_batch(records, logger)

    def _convert_item(
        self,
        item: PipelineLogItem,
        timestamp: datetime,
        event: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PipelineLogItem:
        result = item
        if item.app_name is None:
            result.app_name = self.app_name
        if item.timestamp is None:
            result.timestamp = timestamp
            result.year = str(timestamp.year)
            result.month = "{:02d}".format(timestamp.month)
            result.day = "{:02d}".format(timestamp.day)
            result.hour = "{:02d}".format(timestamp.hour)
        if event is not None:
            result.event = event
        elif item.event is None:
            raise PipelineLoggerValidationError(
                "event is None", extra=ExtraModel(etc={"error_item": item.to_dict()})
            )
        if result.event not in ALLOWED_EVENTS:
            raise PipelineLoggerValidationError(
                f"not allowed event. '{result.event} not in [{ALLOWED_EVENTS}]'",
                ExtraModel(etc={"error_item": item.to_dict()}),
            )
        if item.status == "fail" and not item.error_code:
            item.error_code = "500"

        if status is not None:
            result.status = status
        elif item.status is None:
            raise PipelineLoggerValidationError(
                "status is None", extra=ExtraModel(etc={"error_item": item.to_dict()})
            )
        if isinstance(item.metadata, dict):
            result.metadata = json.dumps(item.metadata, ensure_ascii=False)
        if isinstance(item.extra, dict):
            result.extra = json.dumps(item.extra, ensure_ascii=False)

        if isinstance(item.error_detail, dict):
            result.error_detail = json.dumps(item.error_detail, ensure_ascii=False)
        if isinstance(item.request_body, dict):
            result.req_body = json.dumps(item.request_body, ensure_ascii=False)
        return result
