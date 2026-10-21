import os
from pathlib import Path

import certifi
import grpc
from google.cloud.secretmanager_v1.services.secret_manager_service.transports.grpc import (
    SecretManagerServiceGrpcTransport,
)

import google.auth # type: ignore
from google.cloud import secretmanager


class SecretManager:
    """
    Config GSM 
    Configures the Google Secret Manager 
    This class is used to set up the necessary api key integration 
    """
    def __init__(self):    
        self.credentials, self.project_id = google.auth.default()
        self.data = []

    def __get_secret_version(self, secret_id, version_id="latest"):
        """
        Access the payload for the given secret version if one exists. The version
        can be a version number as a string (e.g. "5") or an alias (e.g. "latest").
        """

        transport = SecretManagerServiceGrpcTransport(
            credentials=self.credentials,
            ssl_channel_credentials=grpc.ssl_channel_credentials(
                root_certificates=Path(certifi.where()).read_bytes()
            ),
        )
        client = secretmanager.SecretManagerServiceClient(transport=transport)

        # Build the resource name of the secret version & return payload
        name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        payload = response.payload.data.decode("UTF-8")
        return payload

    def get_secret_data(self, secret_id):
        """
        Adds secret data to a list for more portability
        """

        api_key = self.__get_secret_version(secret_id=secret_id)
        self.data.append(api_key) 
    
if __name__ == "__main__":
    SecretManager()
