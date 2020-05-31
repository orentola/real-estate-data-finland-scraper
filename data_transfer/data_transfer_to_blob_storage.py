""" 

The purpose of this script is to upload the 
data from daily runs into Azure Data Lake.

By default will look traverse /data/ folder.
Expected to be placed to the same folder as oikotie_scraper.py.
A parameter defines the path to be uplaoded.
Checks if a local configuration file exists that
contains information when this was last run.
Any file that was created in that folder structure
after the time it was last run will be uploaded.

TODO:
- Check if the blob is older at destination instead of local checks

"""

import os
import time

from datetime import datetime
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

DELETE_AFTER_UPLOAD = False
DISREGARD_MODIFIED_DATE = False

try:
	#CONN_STRING = os.getenv("oikotie-scraper-azure-blob-connstring")
	CONN_STRING = os.getenv("CONN_STRING")
except:
	print("Connection string environmental variables not set. Exiting.")
	exit()

PATH = os.getcwd()
STORAGE_ACCOUNT_NAME = "generaldatastore123"
CONTAINER_NAME = "oikotie-scraped"
OVERWRITE_EXISTING_BLOB = True

try:
	BLOB_SERVICE_CLIENT = BlobServiceClient.from_connection_string(CONN_STRING)
except Exception as e:
	print("Error opening blob service client, exiting.")
	print(str(e))
	exit()

# The first line represents the datetime when last run in format YYYY-MM-DD HH:MM:SS
try:
	LAST_RUN_DATETIME = datetime.strptime(open("data_transfer.conf", "r").readline().rstrip("\n"), "%Y-%m-%d %H:%M:%S")
except:
	LAST_RUN_DATETIME = datetime.min

"""

Careful with this function, it will upload everything in the
folder structure. Make sure you call this with intended parameters.

"""

def traverse_folder_structure_and_upload(subfolder="data"):
	# Get all subdirectories
	current_folders = next(os.walk(subfolder))[1] 
	
	for f in current_folders:
		traverse_folder_structure_and_upload(os.path.join(subfolder, f))

	# Get all files, these are not paths
	file_names_to_upload = next(os.walk(subfolder))[2] 
	
	file_path = next(os.walk(subfolder))[0]

	for u in file_names_to_upload:
		full_path = os.path.join(file_path, u)
		last_modified = datetime.fromtimestamp(os.path.getmtime(full_path)) if DISREGARD_MODIFIED_DATE is False else ""
		
		# or short circuits the clause if DISREGARD_MODIFIED_DATE is False
		if (DISREGARD_MODIFIED_DATE or last_modified > LAST_RUN_DATETIME):
			print("Uploading file: " + full_path)
			upload_file(os.path.join(file_path, u))
		else:
			print("Skipped file due to timestamp: " + full_path)

def upload_file(path):
	try:
		with open(path, "rb") as data:
			blob_client = BLOB_SERVICE_CLIENT.get_blob_client(container=CONTAINER_NAME, blob=path)
			blob_client.upload_blob(data, overwrite=OVERWRITE_EXISTING_BLOB)
		if DELETE_AFTER_UPLOAD is True:
			print("Delete after upload is ENABLED. Deleting the uploaded file.")
			os.remove(path)
	except Exception as e:
		print("Error either uploading or downloading file: " + str(path))
		print(str(e))

def main():
	while True:
		print("Checking if new files and uploads if new found.")
		time_start = datetime.now()

		try:
			with open("data_transfer.conf", "w") as f:
				f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			traverse_folder_structure_and_upload()
		except:
			print("Catch all exception in main.")
		
		time_end = datetime.now()
		elapsed = round((time_end - time_start).seconds/60/60,6)
		sleeptime = 24 - elapsed

		print("Run took: " + str(elapsed) + ", sleeping for: " + str(sleeptime) + " hours.")
		time.sleep(sleeptime * 60 * 60)

main()

