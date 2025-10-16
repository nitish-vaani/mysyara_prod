import asyncio
import logging
import os

from azure.storage.blob.aio import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError, AzureError

logger = logging.getLogger(__name__)


class BlobConnector:
    def __init__(self, container_name: str):
        """Initialize BlobService client and container name."""
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("AZURE_STORAGE_CONNECTION_STRING env var not set")

        self.blob_service_client = BlobServiceClient.from_connection_string(
            connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            container_name
        )
        self.container_name = container_name
    
    async def upload_file_async(self, file_path: str, blob_name: str):
        """Uploads a file to Azure Blob asynchronously."""

        blob_client = self.container_client.get_blob_client(blob_name)

        print("Uploading to Azure Blob Storage:", blob_client.url)
        with open(file_path, "rb") as data:
            await blob_client.upload_blob(data, overwrite=True)

        logger.info(f"Uploaded {file_path} to azure://{self.container_name}/{blob_name}")
        return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

    def upload_file(self, file_path: str, blob_name: str):
        """Uploads a file to Azure Blob synchronously."""
        try:
            with open(file_path, "rb") as data:
                self.container_client.upload_blob(
                    name=blob_name, data=data, overwrite=True
                )
            logger.info(f"File uploaded to Azure Blob: {blob_name}")
            return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
        except AzureError as e:
            logger.error(f"Failed to upload {file_path} to Azure Blob: {str(e)}")
            return None

    async def fetch_file_async(self, blob_name: str):
        """Fetches a file from Azure Blob asynchronously."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            stream = await blob_client.download_blob()
            data = await stream.readall()
            return data
        except ResourceNotFoundError:
            logger.error(f"Blob {blob_name} not found in {self.container_name}")
            return None
        except AzureError as e:
            logger.error(f"Azure Blob fetch failed: {str(e)}")
            return None

    def fetch_file(self, blob_name: str):
        """Fetches a file from Azure Blob synchronously."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            stream = blob_client.download_blob()
            return stream.readall()
        except Exception as e:
            logger.error(f"Failed to fetch {blob_name} from Azure Blob: {e}")
            return None


if __name__=="__main__":
    print("Hello World")

    async def main():
        connector = BlobConnector(container_name="vaanirecordings")
        blob_name = "EG_3dSFdibWhMyT.json"
        blob_name_2 = "room-2zZdDf4E2EVQ-+917055888820_00005.ts"



########## upload file test ########################

        # upload_file_name = "1002.mp3"
        upload_file_name = "maqsam_inbound_971502942843_242298124_1760168812.txt"
        upload_data = await connector.upload_file_async(upload_file_name, f"transcripts/mysyara/2025/October/{upload_file_name}")
        print(f"Uploaded file URL: {upload_data}")
        if upload_data:
            print(f"Upload successful {len(upload_data)} bytes")
        else:
            print("Upload failed")
##############################################################

########## fetch file test ###################
        # audio_blob_name = "mp3/1002.mp3"
        data = await connector.fetch_file_async(upload_file_name)
        if data:
            # Check if it's a binary file (like .ts video files)
            print("\n"*3)
            print(f"Successfully fetched {len(data)} bytes")
            print("\n"*3)
        else:
            print("Failed to fetch file")
##############################################################

    asyncio.run(main())