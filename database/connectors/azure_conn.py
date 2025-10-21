# import asyncio
# import logging
# import os

# from azure.storage.blob.aio import BlobServiceClient
# from azure.core.exceptions import ResourceNotFoundError, AzureError

# logger = logging.getLogger(__name__)


# class BlobConnector:
#     def __init__(self, container_name: str):
#         """Initialize BlobService client and container name."""
#         connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
#         if not connection_string:
#             raise ValueError("AZURE_STORAGE_CONNECTION_STRING env var not set")

#         self.blob_service_client = BlobServiceClient.from_connection_string(
#             connection_string
#         )
#         self.container_client = self.blob_service_client.get_container_client(
#             container_name
#         )
#         self.container_name = container_name
    
#     async def upload_file_async(self, file_path: str, blob_name: str):
#         """Uploads a file to Azure Blob asynchronously."""

#         blob_client = self.container_client.get_blob_client(blob_name)

#         # print("Uploading to Azure Blob Storage:", blob_client.url)
#         with open(file_path, "rb") as data:
#             await blob_client.upload_blob(data, overwrite=True)

#         logger.info(f"Uploaded {file_path} to azure://{self.container_name}/{blob_name}")
#         return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"

#     def upload_file(self, file_path: str, blob_name: str):
#         """Uploads a file to Azure Blob synchronously."""
#         try:
#             with open(file_path, "rb") as data:
#                 self.container_client.upload_blob(
#                     name=blob_name, data=data, overwrite=True
#                 )
#             logger.info(f"File uploaded to Azure Blob: {blob_name}")
#             return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
#         except AzureError as e:
#             logger.error(f"Failed to upload {file_path} to Azure Blob: {str(e)}")
#             return None

#     async def fetch_file_async(self, blob_name: str):
#         """Fetches a file from Azure Blob asynchronously."""
#         try:
#             blob_client = self.container_client.get_blob_client(blob_name)
#             stream = await blob_client.download_blob()
#             data = await stream.readall()
#             return data
#         except ResourceNotFoundError:
#             logger.error(f"Blob {blob_name} not found in {self.container_name}")
#             return None
#         except AzureError as e:
#             logger.error(f"Azure Blob fetch failed: {str(e)}")
#             return None

#     def fetch_file(self, blob_name: str):
#         """Fetches a file from Azure Blob synchronously."""
#         try:
#             blob_client = self.container_client.get_blob_client(blob_name)
#             stream = blob_client.download_blob()
#             return stream.readall()
#         except Exception as e:
#             logger.error(f"Failed to fetch {blob_name} from Azure Blob: {e}")
#             return None





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

        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = None
        self.container_client = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.blob_service_client = BlobServiceClient.from_connection_string(
            self.connection_string
        )
        self.container_client = self.blob_service_client.get_container_client(
            self.container_name
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensure cleanup"""
        await self.close()
    
    async def close(self):
        """Explicitly close the blob service client"""
        if self.blob_service_client:
            await self.blob_service_client.close()
    
    async def _ensure_client(self):
        """Ensure client is initialized"""
        if not self.blob_service_client:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )
            self.container_client = self.blob_service_client.get_container_client(
                self.container_name
            )
    
    async def upload_file_async(self, file_path: str, blob_name: str):
        """Uploads a file to Azure Blob asynchronously."""
        await self._ensure_client()
        
        blob_client = self.container_client.get_blob_client(blob_name)

        try:
            with open(file_path, "rb") as data:
                await blob_client.upload_blob(data, overwrite=True)

            logger.info(f"Uploaded {file_path} to azure://{self.container_name}/{blob_name}")
            return f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}"
        finally:
            # Close the client after each operation to prevent memory leaks
            await self.close()

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
        await self._ensure_client()
        
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
        finally:
            # Close the client after each operation
            await self.close()

    def fetch_file(self, blob_name: str):
        """Fetches a file from Azure Blob synchronously."""
        try:
            blob_client = self.container_client.get_blob_client(blob_name)
            stream = blob_client.download_blob()
            return stream.readall()
        except Exception as e:
            logger.error(f"Failed to fetch {blob_name} from Azure Blob: {e}")
            return None