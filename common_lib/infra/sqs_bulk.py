import math
import uuid
from base64 import b64encode
from datetime import datetime, timedelta
from typing import NamedTuple, Optional

import boto3
from botocore.exceptions import ClientError

from common_lib.errors import ErrorWithExtraInfo
from common_lib.errors.exception import ExtraModel
from common_lib.models.message import ModelMessage, ModelMessageHeader

SQS_MAX_BYTES = 180 * 1024  # 256 KB - 5KB (여유분)
SQS_MAX_ENTRIES = 10  # SQS Max entry size


class SQSClient:
    def __init__(
        self,
        sqs_name: str,
        max_num_of_message: int = 10,
        wait_time_seconds: int = 20,
        endpoint_url: str = None,
        boto3_sqs_resource: Optional[any] = None,
    ):
        """
        SQS Client를 초기화합니다.
        :param sqs_name: SQS Queue Name
        :param max_num_of_message: 동시에 수신할 message 수 (기본: 1, 최대: 10)
        :param wait_time_seconds: long pooling 시 최대로 wait 할 시간: (기본: 20, 최소: 0, 최대: 20)
        """
        self.sqs_name = sqs_name
        self.max_num_of_message = max_num_of_message
        self.wait_time_seconds = wait_time_seconds
        self.conn_variable = dict()
        if endpoint_url is not None:
            self.conn_variable["endpoint_url"] = endpoint_url

        self.conn = boto3.session.Session()

        if boto3_sqs_resource is not None:
            self.sqs = boto3_sqs_resource
        else:
            self.sqs = self.conn.resource("sqs", **self.conn_variable)

        try:
            self.queue = self.sqs.get_queue_by_name(QueueName=self.sqs_name)
            if not self.queue:
                raise Exception(
                    "no response from get_queue_by_name(%s)" % self.sqs_name
                )
            self.queue_url = self.queue.url
        except ClientError as e:
            raise e

    def __recv_up_to(
        self, max_num_of_message: int, wait_time_seconds: int = None
    ) -> list:
        if wait_time_seconds is None:
            _wait_time_seconds = self.wait_time_seconds
        else:
            _wait_time_seconds = wait_time_seconds

        num_to_be_received = min(max_num_of_message, 10)
        msgs = self.queue.receive_messages(
            AttributeNames=[
                "ApproximateFirstReceiveTimestamp",
                "SentTimestamp",
                "ApproximateReceiveCount",
            ],
            MaxNumberOfMessages=num_to_be_received,
            WaitTimeSeconds=_wait_time_seconds,
        )
        if len(msgs) < 1 or len(msgs) >= max_num_of_message:
            return msgs

        while True:
            num_to_be_received = min(max_num_of_message - len(msgs), 10)
            if num_to_be_received < 1:
                break

            _msgs = self.queue.receive_messages(
                AttributeNames=[
                    "ApproximateFirstReceiveTimestamp",
                    "SentTimestamp",
                    "ApproximateReceiveCount",
                ],
                MaxNumberOfMessages=num_to_be_received,
                WaitTimeSeconds=0,
            )

            if len(_msgs) < 1:
                break

            msgs.extend(_msgs)
        return msgs

    def recv(
        self, timeout: int = None, wait_time_seconds: int = None
    ) -> list[ModelMessage]:
        """
        Receive message from SQS
        :param timeout: (optional) Timeout이 None이 아닐 경우, sent time 기준으로 timeout 된 message는 처리 없이 삭제함
        :param wait_time_seconds: (optional) Long pooling 제어를 위한 파라메터
        :return: (message header, body) 오류 발생시에는 (None, None)
        """
        if wait_time_seconds is None:
            _wait_time_seconds = self.wait_time_seconds
        else:
            _wait_time_seconds = wait_time_seconds

        msgs = self.__recv_up_to(
            max_num_of_message=self.max_num_of_message,
            wait_time_seconds=_wait_time_seconds,
        )

        if msgs is None:
            return []

        parsed_messages = []

        for msg in msgs:
            msg_attributes = msg.attributes
            if "ApproximateFirstReceiveTimestamp" in msg_attributes:
                msg_attributes[
                    "ApproximateFirstReceiveTimestamp"
                ] = datetime.fromtimestamp(
                    float(msg.attributes["ApproximateFirstReceiveTimestamp"]) / 1000
                )
            if "SentTimestamp" in msg_attributes:
                msg_attributes["SentTimestamp"] = datetime.fromtimestamp(
                    float(msg.attributes["SentTimestamp"]) / 1000
                )

            header = ModelMessageHeader(
                id=msg.message_id,
                queue_url=msg.queue_url,
                handle=msg.receipt_handle,
                attributes=msg_attributes,
                num_trial=int(msg_attributes.get("ApproximateReceiveCount", "1")),
            )

            if timeout is not None:
                timeout_at = msg_attributes["SentTimestamp"] + timedelta(
                    seconds=timeout
                )
                if datetime.now() >= timeout_at:
                    self.ack(header)
                    raise TimeoutError(
                        f"[msg_id: {msg.message_id}] Message Timeout (> {timeout} sec), dropped"
                    )

            parsed_messages.append(ModelMessage(header=header, body=msg.body))
        return parsed_messages

    def ack(self, message_header: ModelMessageHeader) -> None:
        """
        처리가 완료된 메시지를 삭제합니다.
        :param message_header:
        :return: None
        """
        self.queue.delete_messages(
            Entries=[{"Id": message_header.id, "ReceiptHandle": message_header.handle}]
        )

    def ack_batch(self, message_headers: list[ModelMessageHeader]) -> None:
        """
        처리가 완료된 여러 메시지를 삭제합니다.
        :param message_headers:
        :return:
        """
        num_chunks = math.ceil(len(message_headers) / float(SQS_MAX_ENTRIES))
        sp = 0
        for i in range(num_chunks):
            chunk_size = min(
                SQS_MAX_ENTRIES, len(message_headers) - i * SQS_MAX_ENTRIES
            )
            chunk = message_headers[sp : (sp + chunk_size)]
            sp += chunk_size
            self.queue.delete_messages(
                Entries=[{"Id": x.id, "ReceiptHandle": x.handle} for x in chunk]
            )

    def publish(self, body: str) -> dict:
        """

        :param body:
        :return:
        """
        response = self.queue.send_message(MessageBody=body, DelaySeconds=0)
        return response

    @staticmethod
    def __make_chunk_to_publish(entries: list[str]) -> list[list[str]]:
        """
        SQS의 batch send message 에는 다음 두 가지 제약이 있다.
         + 한 번에 send 가능한 총 message 수는 10개 이내
         + 한 번에 send 가능한 총 message size는 256 KB 이내
        위 제약사항을 준수하면서 원하는 수량의 message 를 적절히 나누어주는 역할을 한다.
        :param entries: 보내고싶은 모든 message
        :return: 적절히 나누어진 message
        """
        lengths = [len(b64encode(x.encode("utf-8"))) for x in entries]
        chunks = []

        class State(NamedTuple):
            start_idx: int = 0
            end_idx: int = 1
            length: int = 0
            num_entry: int = 0

        state = State()

        for idx, length in enumerate(lengths):
            next_state = State(
                start_idx=state.start_idx,
                end_idx=state.end_idx + 1,
                length=state.length + length,
                num_entry=state.num_entry + 1,
            )
            if (
                next_state.num_entry >= SQS_MAX_ENTRIES
                or next_state.length >= SQS_MAX_BYTES
            ):
                chunks.append(entries[state.start_idx : state.end_idx])
                state = State(
                    start_idx=state.end_idx,
                    end_idx=state.end_idx + 1,
                    length=length,
                    num_entry=0,
                )
            else:
                state = next_state
        if state.num_entry > 0:
            chunks.append(entries[state.start_idx : state.end_idx])
        return chunks

    def publish_batch(self, bodies: list[str], logger=None):
        chunks = self.__make_chunk_to_publish(bodies)
        for chunk in chunks:
            try:
                self.queue.send_messages(
                    Entries=[
                        {
                            "Id": str(uuid.uuid4()),
                            "MessageBody": x,
                        }
                        for x in chunk
                    ]
                )
            except Exception as e:
                if logger:
                    logger.error(
                        "publish_batch_error",
                        exc_info=e,
                        extra={
                            "chunk": chunk,
                        },
                    )
                raise ErrorWithExtraInfo(
                    message="", exc_info=e, extra=ExtraModel(etc={"chunk": chunk})
                )
