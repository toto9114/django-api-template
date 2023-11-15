import boto3
from typing import Optional
from common_lib.utils.singleton import Singleton, initialize_once


class S3Session(Singleton):
    @initialize_once
    def __init__(self, name: str = "default"):
        self.name = name
        self.session: Optional[boto3.Session] = None
        self.s3 = None

    def initialize(self):
        self.session = boto3.Session()
        self.s3 = self.session.client("s3")

    def get_s3(self):
        if self.s3 is None:
            raise Exception("S3Session is not initialized")
        return self.s3
