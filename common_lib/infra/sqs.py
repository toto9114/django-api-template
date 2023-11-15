import json
import uuid
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from botocore.client import Config


class SQS:
    MAX_SQS_COUNT = 10

    def __init__(
        self,
        que_name,
        boto3_read_timeout: float = 2.0,
        boto3_connect_timeout: float = 2.0,
        boto3_max_retry: int = 10,
        boto3_max_pool_connections: int = 30,
        boto3_sqs_client: Optional[any] = None,
    ):
        if boto3_sqs_client is not None:
            self.sqs = boto3_sqs_client
        else:
            self.sqs = boto3.client(
                "sqs",
                config=Config(
                    read_timeout=boto3_read_timeout,
                    connect_timeout=boto3_connect_timeout,
                    max_pool_connections=boto3_max_pool_connections,
                    retries={"max_attempts": boto3_max_retry},
                ),
            )
        self.sqs_url = self.sqs.get_queue_url(QueueName=que_name)

    def send_message(self, message):
        """
        :param message: dict
        :return:
        """
        self.sqs.send_message(
            QueueUrl=self.sqs_url["QueueUrl"], MessageBody=json.dumps(message)
        )

    def send_message_batch(self, messages: list):
        self.sqs.send_message_batch(
            QueueUrl=self.sqs_url["QueueUrl"],
            Entries=[
                {"Id": str(uuid.uuid4()), "MessageBody": json.dumps(x)}
                for x in messages
            ],
        )

    def send_message_batch_no_wait(self, messages: list):
        for idx in range(0, len(messages), SQS.MAX_SQS_COUNT):
            self.sqs.send_message_batch(
                QueueUrl=self.sqs_url["QueueUrl"],
                Entries=[
                    {"Id": str(uuid.uuid4()), "MessageBody": json.dumps(x)}
                    for x in messages[idx : idx + SQS.MAX_SQS_COUNT]
                ],
            )

    def receive_message(self) -> dict:
        """
        Default getting message number is 1
        Raw received message is like below
        {
          'Messages': [
            {
              'Body': '{...}',
              'MD5OfBody': 'c24fd2b39b48675b320fa89a01902627',
              'MessageId': '28acfc56-d259-459d-a3dc-55bb8a1db45e',
              'ReceiptHandle': 'AQEBiXQ3h.....Ob/XJVzmoFog=='
            }
          ],
          'ResponseMetadata': {
            'HTTPHeaders': {
              'content-length': '890',
              'content-type': 'text/xml',
              'date': 'Tue, 20 Aug 2019 08:05:04 GMT',
              'x-amzn-requestid': '930a7db0-46f5-559e-a382-2865ed057bdf'
            },
            'HTTPStatusCode': 200,
            'RequestId': '930a7db0-46f5-559e-a382-2865ed057bdf',
            'RetryAttempts': 0
          }
        }
        :return: A message dict from 'Messages' list
        {
          'Body': '{...}',
          'MD5OfBody': 'c24fd2b39b48675b320fa89a01902627',
          'MessageId': '28acfc56-d259-459d-a3dc-55bb8a1db45e',
          'ReceiptHandle': 'AQEBiXQ3h.....Ob/XJVzmoFog=='
        }
        """
        response = dict()
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.sqs_url["QueueUrl"],
                AttributeNames=["ApproximateReceiveCount"],
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        message = response.get("Messages", [dict()])
        return message[0]

    def receive_message_batch(self) -> list:
        """
        Default getting message number is 1
        Raw received message is like below
        {
          'Messages': [
            {
              'Body': '{...}',
              'MD5OfBody': 'c24fd2b39b48675b320fa89a01902627',
              'MessageId': '28acfc56-d259-459d-a3dc-55bb8a1db45e',
              'ReceiptHandle': 'AQEBiXQ3h.....Ob/XJVzmoFog=='
            }
          ],
          'ResponseMetadata': {
            'HTTPHeaders': {
              'content-length': '890',
              'content-type': 'text/xml',
              'date': 'Tue, 20 Aug 2019 08:05:04 GMT',
              'x-amzn-requestid': '930a7db0-46f5-559e-a382-2865ed057bdf'
            },
            'HTTPStatusCode': 200,
            'RequestId': '930a7db0-46f5-559e-a382-2865ed057bdf',
            'RetryAttempts': 0
          }
        }
        :return: A message dict from 'Messages' list
        {
          'Body': '{...}',
          'MD5OfBody': 'c24fd2b39b48675b320fa89a01902627',
          'MessageId': '28acfc56-d259-459d-a3dc-55bb8a1db45e',
          'ReceiptHandle': 'AQEBiXQ3h.....Ob/XJVzmoFog=='
        }
        """
        response = dict()
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.sqs_url["QueueUrl"],
                AttributeNames=["ApproximateReceiveCount"],
                MaxNumberOfMessages=SQS.MAX_SQS_COUNT,
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        messages = response.get("Messages", list())
        return messages

    def receive_message_batch_no_wait(self, max_num) -> list:
        """
        Default getting message number is 1
        Raw received message is like below
        {
          'Messages': [
            {
              'Body': '{...}',
              'MD5OfBody': 'c24fd2b39b48675b320fa89a01902627',
              'MessageId': '28acfc56-d259-459d-a3dc-55bb8a1db45e',
              'ReceiptHandle': 'AQEBiXQ3h.....Ob/XJVzmoFog=='
            }
          ],
          'ResponseMetadata': {
            'HTTPHeaders': {
              'content-length': '890',
              'content-type': 'text/xml',
              'date': 'Tue, 20 Aug 2019 08:05:04 GMT',
              'x-amzn-requestid': '930a7db0-46f5-559e-a382-2865ed057bdf'
            },
            'HTTPStatusCode': 200,
            'RequestId': '930a7db0-46f5-559e-a382-2865ed057bdf',
            'RetryAttempts': 0
          }
        }
        :return: A message dict from 'Messages' list
        {
          'Body': '{...}',
          'MD5OfBody': 'c24fd2b39b48675b320fa89a01902627',
          'MessageId': '28acfc56-d259-459d-a3dc-55bb8a1db45e',
          'ReceiptHandle': 'AQEBiXQ3h.....Ob/XJVzmoFog=='
        }
        """
        results = list()
        while True:
            message_count = min(max_num, SQS.MAX_SQS_COUNT)
            if message_count:
                response = self.sqs.receive_message(
                    QueueUrl=self.sqs_url["QueueUrl"],
                    AttributeNames=["ApproximateReceiveCount"],
                    MaxNumberOfMessages=message_count,
                    WaitTimeSeconds=0,
                )
                messages = response.get("Messages", None)
                if messages:
                    results += messages
                    max_num -= len(messages)
                else:
                    break
            else:
                break
        return results

    def delete_message(self, message):
        self.sqs.delete_message(
            QueueUrl=self.sqs_url["QueueUrl"],
            ReceiptHandle=message["ReceiptHandle"],
        )

    def delete_message_batch(self, messages):
        self.sqs.delete_message_batch(
            QueueUrl=self.sqs_url["QueueUrl"],
            Entries=[
                {"Id": x["MessageId"], "ReceiptHandle": x["ReceiptHandle"]}
                for x in messages
            ],
        )

    def delete_message_batch_no_wait(self, messages):
        for idx in range(0, len(messages), SQS.MAX_SQS_COUNT):
            self.sqs.delete_message_batch(
                QueueUrl=self.sqs_url["QueueUrl"],
                Entries=[
                    {"Id": x["MessageId"], "ReceiptHandle": x["ReceiptHandle"]}
                    for x in messages[idx : idx + SQS.MAX_SQS_COUNT]
                ],
            )

    def get_queue_attributes(self):
        response = None
        try:
            response = self.sqs.get_queue_attributes(
                QueueUrl=self.sqs_url["QueueUrl"], AttributeNames=["All"]
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
        messages = None
        if response:
            messages = response.get("Attributes", None)
        return messages
