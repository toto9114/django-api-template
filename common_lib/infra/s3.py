import boto3
from typing import Tuple, Union
from botocore.exceptions import ClientError
from botocore.client import Config


class S3:
    def __init__(
        self,
        bucket,
        boto3_read_timeout: float = 20.0,
        boto3_connect_timeout: float = 10.0,
        boto3_max_retry: int = 10,
        boto3_max_pool_connections: int = 30,
    ):
        self.client = boto3.client(
            "s3",
            config=Config(
                read_timeout=boto3_read_timeout,
                connect_timeout=boto3_connect_timeout,
                max_pool_connections=boto3_max_pool_connections,
                retries={"max_attempts": boto3_max_retry},
            ),
        )
        try:
            result = self.client.get_bucket_location(Bucket=bucket)
        except ClientError as e:
            raise Exception(
                "boto3 client error in get_bucket_location_of_s3: " + e.__str__()
            )
        except Exception as e:
            raise Exception(
                "Unexpected error in get_bucket_location_of_s3 function: " + e.__str__()
            )

        self.region_name = result.get("LocationConstraint", "ap-northeast-2")
        self.bucket_name = bucket

    def put_image(
        self,
        img_path: str,
        data: bytes,
        bucket_name: str = None,
        content_type: str = "",
    ) -> Tuple[bool, Union[ClientError, None]]:
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name
            self.client.put_object(
                Bucket=bucket_name, Key=img_path, Body=data, ContentType=content_type
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return False, e

        return True, None

    def get_image(self, img_path: str, bucket_name: str = None):
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name
            result = self.client.get_object(Bucket=bucket_name, Key=img_path)
            data = result["Body"].read(result["ContentLength"])

        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

        return data

    def put_file(
        self, file_name: str, data, folder: str = None, bucket_name: str = None
    ):
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name
            file_path = file_name if folder is None else folder + "/" + file_name
            self.client.put_object(Bucket=bucket_name, Key=file_path, Body=data)
        except ClientError as e:
            print(e.response["Error"]["Message"])
            raise Exception(e.response["Error"]["Message"])

        return (
            f"https://{bucket_name}.s3."
            + self.region_name
            + ".amazonaws.com/"
            + file_path
        )

    def rm_file(self, folder, path: str, bucket_name: str = None):
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name
            file_path = path if folder is None else folder + "/" + path
            self.client.delete_object(Bucket=bucket_name, Key=file_path)

            print("{} DELETED -".format(file_path))
            return True

        except ClientError as e:
            print(e.response["Error"]["Message"])
            return False

    def rm_folder(self, folder, bucket_name: str = None):
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name

            objects_to_delete = self.client.list_objects(
                Bucket="MyBucket", Prefix=folder
            )
            delete_keys = dict()
            delete_keys["Objects"] = [
                {"Key": k}
                for k in [obj["Key"] for obj in objects_to_delete.get("Contents", [])]
            ]
            self.client.delete_objects(Bucket=bucket_name, Delete=delete_keys)
            print("{} DELETED -".format(folder))
            return True

        except ClientError as e:
            print(e.response["Error"]["Message"])
            return False

    def get_file(self, file_name: str, folder: str = None, bucket_name: str = None):
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name
            file_path = file_name if folder is None else folder + "/" + file_name
            print(bucket_name + "," + file_path)
            result = self.client.get_object(Bucket=bucket_name, Key=file_path)
            data = result["Body"].read(result["ContentLength"])
            return data

        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

    def exist_file(self, file_name: str, folder: str = None, bucket_name: str = None):
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name
            file_path = file_name if folder is None else folder + "/" + file_name
            print(bucket_name + "," + file_path)
            res = self.client.list_objects_v2(
                Bucket=bucket_name, Prefix=file_path, MaxKeys=1
            )
            return "Contents" in res
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

    def get_file_list_all(self, folder: str = "", bucket_name: str = None):
        try:
            bucket_name = self.bucket_name if not bucket_name else bucket_name
            url_encoded_folder = folder
            print(bucket_name + ", " + url_encoded_folder)
            pages = self.client.list_objects(
                Bucket=bucket_name, Prefix=url_encoded_folder
            )["Contents"]
            return pages if pages else None
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

    def create_multipart_upload(self, bucket_name: str = None, key_name: str = ""):
        bucket_name = self.bucket_name if not bucket_name else bucket_name
        try:
            create_multipart_upload_response = self.client.create_multipart_upload(
                Bucket=bucket_name, Key=key_name
            )
            return (
                create_multipart_upload_response["UploadId"]
                if create_multipart_upload_response
                else None
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

    def put_multipart_upload(
        self,
        bucket_name: str = None,
        key_name: str = "",
        upload_id: str = None,
        part_number: int = 1,
        data: bytes = None,
    ):
        bucket_name = self.bucket_name if not bucket_name else bucket_name
        try:
            upload_part_response = self.client.upload_part(
                Bucket=bucket_name,
                Key=key_name,
                PartNumber=part_number,
                UploadId=upload_id,
                Body=data,
            )
            return upload_part_response["ETag"] if upload_part_response else None
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

    def complete_multipart_upload(
        self,
        bucket_name: str = None,
        key_name: str = "",
        upload_id: str = None,
        parts: dict = None,
    ):
        bucket_name = self.bucket_name if not bucket_name else bucket_name
        try:
            self.client.complete_multipart_upload(
                Bucket=bucket_name,
                Key=key_name,
                UploadId=upload_id,
                MultipartUpload=parts,
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None

    def get_file_add_pre_signed_url(
        self,
        bucket_name: str = None,
        key_name: str = "",
        valid_time: int = 60,
    ):
        bucket_name = self.bucket_name if not bucket_name else bucket_name
        try:
            response = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key_name},
                ExpiresIn=valid_time,
            )
            return response
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None
