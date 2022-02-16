from datetime import datetime
import json
import hashlib
import logging.config
import os
from pathlib import Path
import re
import shutil
import traceback

from pprint import pprint
import boto3

from cur_extractor.Config import Config as configure

# logging.config.fileConfig(fname = 'cur_extractor/logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class S3HandlerClass(object):

    def __init__(self,
            storage_id,
            arn,
            bucket_name
    ):
        self.storage_id = storage_id
        self.arn = arn
        self.bucket_name = bucket_name
        self.set_session()
    
    def set_session(self):
        """
        Set attributes with a new session.
        """

        role_credentials = self.get_role_credentials()

        try:
            self.s3 = boto3.resource(
                's3',
                aws_access_key_id = role_credentials['AccessKeyId'],
                aws_secret_access_key = role_credentials['SecretAccessKey'],
                aws_session_token = role_credentials['SessionToken']
            )
            self.expiration = role_credentials["Expiration"]
            self.bucket = self.s3.Bucket(self.bucket_name)
        except Exception as e:
            logger.error(f"Could not connect to S3 - {e}")
            raise e from e

        

    def get_role_credentials(self):
        """
        Return the STS assumed role credentials.
        """
        try:
            sts_client = boto3.client(
                'sts',
                aws_access_key_id=os.getenv('STS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('STS_SECRET_ACCESS_KEY')
            )

            now = datetime.now()
            session_key = hashlib.md5(now.isoformat().encode('utf-8')).hexdigest()

            role = sts_client.assume_role(
                RoleArn=self.arn,
                RoleSessionName=session_key,
                ExternalId=os.getenv('EXTERNAL_ID')
            )

            return role['Credentials']
        except Exception as e:
            logger.error(f"Could not assume role from STS - {e}")
            raise e from e

    def get_object_as_json(self, key):
        """
        Return a JSON representation of the object's data.
        """
        obj = self.bucket.Object(
            key=key
        )
        return json.loads(obj.get()["Body"].read())

    def get_objects_list(self, prefix=""):
        """
        Returns a list of objects with the given prefix.
        """
        return self.bucket.objects.filter(Prefix=prefix)

    def download_single_CUR_data(self, report_key, file_name):
        """
        Download CUR data from S3 and return its download path.
        """
        # Create folder to download CUR data
        download_folder_path = self.get_download_path(self.storage_id)
        self.make_temp_dir(download_folder_path)

        # Create the download path
        download_file_path = os.path.join(download_folder_path, file_name)

        self.bucket.download_file(
            Key = report_key,
            Filename = download_file_path,
        )

        return download_file_path

    def upload_CUR_data(self, file_path):
        """
        Upload CUR data to S3
        """
        try:
            object_key = file_path[file_path.rfind('/')+1:]
            object_key = object_key.replace('&&', '/')
            self.bucket.upload_file(Filename=file_path, Key=object_key)
        except Exception as e:
            logger.error(f'Error during upload CUR data to S3 - {e} - {file_path}')
            raise Exception from e

    def get_download_path(self, account_id):
        """
        Make and return the download path for the new file.
        """
        return f"{configure.DOWNLOAD_PATH}/{account_id}"

    def make_temp_dir(self, path):
        """
        Create a temporary folder.
        """
        # Create directory if download path does not exist
        if not(os.path.isdir(path) and os.path.exists(path)):
            try:
                os.makedirs(path)
            except OSError as e:
                logger.error(f"Creation of the directory {path} failed")
                raise Exception(f"Creation of the directory {path} failed") from e
            logger.info("Successfully created the directory path")

        return path

    def remove_download_temp_dir(self):
        """
        Delete the temporary folder
        """
        download_path = configure.DOWNLOAD_PATH

        # Remove temp folder
        if os.path.isdir(download_path) and os.path.exists(download_path):
            try:
                shutil.rmtree(download_path)
            except OSError as e:
                logger.info(f"Deletion of the directory {download_path} failed")
                raise Exception(f"Deletion of the directory {download_path} failed") from e
            logger.info("Successfully deleted the directory {download_path}")

        return True

