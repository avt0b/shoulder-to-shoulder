import logging
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError
from backend.media_service.app.core.config import settings

logger = logging.getLogger(__name__)


class S3Manager:
    def __init__(self):
        self.bucket = settings.AWS_S3_BUCKET
        self.public_url = settings.AWS_PUBLIC_URL.rstrip("/")

        session_kwargs = {
            "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
            "region_name": settings.AWS_S3_REGION,
            "config": Config(signature_version="s3v4", retries={"max_attempts": 3})
        }

        if settings.AWS_S3_ENDPOINT_URL:
            session_kwargs["endpoint_url"] = settings.AWS_S3_ENDPOINT_URL

        try:
            self.client = boto3.client("s3", **session_kwargs)
            logger.info(f"S3 client initialized for bucket: {self.bucket}")
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            raise

    def generate_upload_url(self, file_key: str, content_type: str, expires_in: int = 3600) -> dict:
        try:
            response = self.client.generate_presigned_post(
                Bucket=self.bucket,
                Key=file_key,
                Fields={"Content-Type": content_type},
                Conditions=[
                    {"Content-Type": content_type},
                    ["content-length-range", 0, settings.MAX_FILE_SIZE]
                ],
                ExpiresIn=expires_in
            )
            return {
                "file_key": file_key,
                "upload_url": response["url"],
                "fields": response["fields"],
                "public_url": f"{self.public_url}/{file_key}"
            }
        except ClientError as e:
            logger.error(f"S3 presigned post failed [{file_key}]: {e}")
            raise RuntimeError("Failed to generate upload URL")

    def delete_object(self, file_key: str) -> bool:
        try:
            self.client.delete_object(Bucket=self.bucket, Key=file_key)
            logger.info(f"Deleted file from S3: {file_key}")
            return True
        except ClientError as e:
            logger.error(f"S3 delete failed [{file_key}]: {e}")
            return False

    def get_public_url(self, file_key: str) -> str:
        return f"{self.public_url}/{file_key}"


s3 = S3Manager()
