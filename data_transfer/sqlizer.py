# No need for this right now, downloading data manually.

import os
import time

from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

CONN_STRING = "DefaultEndpointsProtocol=https;AccountName=generaldatastore123;AccountKey=hGZD95QIRPJKF4BnyMjgvS76PVcy29st/dk9TUxgvjbamnuLY38HOmm4pi4rF5LqdqY0L1tjeSN/nFZZunYS4w==;EndpointSuffix=core.windows.net"

STORAGE_ACCOUNT_NAME = "generaldatastore123"
CONTAINER_NAME = "oikotie-scraped"
OVERWRITE_EXISTING_BLOB = True

BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(CONN_STRING)
container_client = BLOB_SERVICE_CLIENT.get_container_client("oikotie-scraped")

blob_list = container_client.list_blobs("data/")

for blob in blob_list:
	if blob["name"].find(".json") > -1:
