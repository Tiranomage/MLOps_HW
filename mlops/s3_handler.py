import boto3
from botocore.exceptions import ClientError
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class S3Manager:
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )

    def download_file(self, bucket_name: str, s3_key: str, local_path: Path) -> None:
        try:
            self.s3_client.download_file(bucket_name, s3_key, str(local_path))
            logger.info(f"Downloaded {s3_key} from {bucket_name} to {local_path}")
        except ClientError as e:
            logger.error(f"Error downloading {s3_key}: {e}")
            raise

    def upload_file(self, local_path: Path, bucket_name: str, s3_key: str) -> None:
        try:
            self.s3_client.upload_file(str(local_path), bucket_name, s3_key)
            logger.info(f"Uploaded {local_path} to {bucket_name}/{s3_key}")
        except ClientError as e:
            logger.error(f"Error uploading {local_path}: {e}")
            raise
