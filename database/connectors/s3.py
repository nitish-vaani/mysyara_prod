import asyncio
import logging
import os

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class S3Connector:
    def __init__(self, bucket_name: str):
        """Initialize S3 client and bucket name."""
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),  # Default to us-east-1
        )
        self.bucket_name = bucket_name

    async def upload_file_async(self, file_path: str, s3_key: str):
        """Uploads a file to S3 asynchronously."""
        try:
            await asyncio.to_thread(
                self.s3_client.upload_file, file_path, self.bucket_name, s3_key
            )
            logger.info(f"Uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        except NoCredentialsError:
            logger.error("AWS credentials not found. Upload failed.")
        except ClientError as e:
            logger.error(f"AWS S3 ClientError: {e.response['Error']['Message']}")
        except Exception as e:
            logger.error(f"Upload failed: {e}")

    def upload_file(self, file_path: str, s3_key: str):
        """
        Upload a file to S3.

        Args:
            file_path (str): Local file path.
            s3_key (str): S3 object key (filename in S3).
        """
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            logger.info(f"File uploaded to S3: s3://{self.bucket_name}/{s3_key}")
            return f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
        except Exception as e:
            logger.error(f"Failed to upload {file_path} to S3: {e}")
            return None

    async def fetch_file_async(self, s3_key: str):
        """Fetches a file from S3 asynchronously."""
        try:
            response = await asyncio.to_thread(
                self.s3_client.get_object, Bucket=self.bucket_name, Key=s3_key
            )
            return response["Body"].read()
        except NoCredentialsError:
            logger.error("AWS credentials not found. Fetch failed.")
            return None
        except ClientError as e:
            logger.error(f"AWS S3 ClientError: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Fetch failed: {e}")
            return None

    def fetch_file(self, s3_key: str):
        """Fetches a file from S3 synchronously."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)
            return response["Body"].read()
        except Exception as e:
            logger.error(f"Failed to fetch {s3_key} from S3: {e}")
            return None
