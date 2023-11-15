import time
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Union
from urllib.parse import urlparse

import boto3
import pandas as pd
from dataclasses_json import DataClassJsonMixin

from common_lib.utils.singleton import singleton


@dataclass
class AthenaQueryStatistics(DataClassJsonMixin):
    EngineExecutionTimeInMillis: Union[int, None] = None
    DataScannedInBytes: Union[int, None] = None
    TotalExecutionTimeInMillis: Union[int, None] = None
    QueryQueueTimeInMillis: Union[int, None] = None
    QueryPlanningTimeInMillis: Union[int, None] = None
    ServiceProcessingTimeInMillis: Union[int, None] = None


@dataclass
class AthenaQueryResult:
    result: pd.DataFrame
    submission_datetime: datetime
    completion_dateTime: datetime
    statistics: AthenaQueryStatistics


class AthenaQueryExecution(Exception):
    pass


@singleton
class AthenaQueryHelper:
    def __init__(self, name: str = "default"):
        self.name = name
        self.athena = None
        self.s3 = None
        self.initialized = False
        self.s3_bucket_name = None
        self.s3_bucket_path_prefix = None
        self.database = None
        self.max_trial = 60
        self.poll_interval_trial = 1.0

    def initialize(
        self,
        s3_bucket_name: str,
        database: str,
        aws_access_key_id: Union[str, None] = None,
        aws_secret_access_key: Union[str, None] = None,
        region_name: str = "ap-northeast-2",
        s3_bucket_path_prefix: str = "python",
        max_trial: int = 60,
        poll_interval_trial: float = 1.0,
    ):
        """
        Initialize Athena Driver
        @param s3_bucket_name: S3 bucket name to store query results
        @param database: Athena Database name
        @param aws_access_key_id:
        @param aws_secret_access_key:
        @param region_name:
        @param s3_bucket_path_prefix: Path prefix in query result bucket (default: python)
        @param max_trial: (default: 10) 결과를 기다릴 횟수
        @param poll_interval_trial: (default: 1.0) polling 주기 (초 단위)
        @return:
        """

        self.database = database
        self.s3_bucket_name = s3_bucket_name
        self.s3_bucket_path_prefix = s3_bucket_path_prefix

        self.conn = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.athena = self.conn.client("athena")
        self.s3 = self.conn.client("s3")

        self.initialized = True
        self.max_trial = max_trial
        self.poll_interval_trial = poll_interval_trial

    def execute_query(self, query: str) -> AthenaQueryResult:
        """
        Athena Query 를 실행합니다.
        실행 시간이 오래 걸리는 query 작업을 수행하는 경우 max_trial, poll_interval 변수 값을 적절히 조절해주어야 합니다.

        @param query: Athena Query

        @return: QueryResult
        """
        if not self.initialized:
            raise Exception(
                "Not Initialized! Please call AthenaQueryHelper.initialize()."
            )

        execution_id = self._dispatch(query)
        response = self._poll(execution_id)
        s3_url = response["QueryExecution"]["ResultConfiguration"]["OutputLocation"]
        return AthenaQueryResult(
            result=self._download(s3_url),
            submission_datetime=response["QueryExecution"]["Status"][
                "SubmissionDateTime"
            ],
            completion_dateTime=response["QueryExecution"]["Status"][
                "CompletionDateTime"
            ],
            statistics=AthenaQueryStatistics.from_dict(
                response["QueryExecution"]["Statistics"]
            ),
        )

    def _dispatch(self, query: str) -> str:
        execution = self.athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": self.database},
            ResultConfiguration={
                "OutputLocation": f"s3://{self.s3_bucket_name}/{self.s3_bucket_path_prefix}"
            },
        )
        return execution["QueryExecutionId"]

    def _poll(self, execution_id: str) -> dict:
        state = "RUNNING"
        max_trial: int = self.max_trial
        while max_trial > 0 and state in ["RUNNING", "QUEUED"]:
            max_trial = max_trial - 1
            response = self.athena.get_query_execution(QueryExecutionId=execution_id)

            if (
                ("QueryExecution" in response)
                and ("Status" in response["QueryExecution"])
                and ("State" in response["QueryExecution"]["Status"])
            ):
                state = response["QueryExecution"]["Status"]["State"]
                if state == "FAILED":
                    raise AthenaQueryExecution(
                        response["QueryExecution"]["Status"]["StateChangeReason"]
                    )
                elif state == "SUCCEEDED":
                    return response
            time.sleep(self.poll_interval_trial)
        raise Exception("Timeout!")

    def _download(self, s3_url: str) -> pd.DataFrame:
        parsed = urlparse(s3_url)
        response = self.s3.get_object(Bucket=parsed.netloc, Key=parsed.path[1:])
        return pd.read_csv(BytesIO(response["Body"].read()))
