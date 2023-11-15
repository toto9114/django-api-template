def split_s3_path(s3_path: str) -> (str, str):
    path_parts = s3_path.replace("s3://", "").replace("S3://", "").split("/")
    bucket = path_parts.pop(0)
    key = "/".join(path_parts)
    return bucket, key
