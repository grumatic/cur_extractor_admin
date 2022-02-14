from datetime import datetime
import json
import logging.config
import os
from pathlib import Path
import re
import shutil
import traceback

import boto3

from cur_extractor.Config import Config as configure

# logging.config.fileConfig(fname = 'cur_extractor/logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class S3HandlerClass(object):

    def __init__(self, access_key, secret_key, storage_id, bucket_name= None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.storage_id = storage_id
        self.bucket_name = bucket_name

        try:
            self.s3 = boto3.client('s3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key)
        except Exception as e:
            logger.error("s3 connection error")
            raise e

    def get_bucket(self):
        return self.s3.bucket(self.bucket_name)

    def get_object_as_json(self, key):
        return json.loads(self.s3.get_object(Bucket=self.bucket_name,
                                                Key=key)["Body"].read())


    def get_objects_list(self, prefix=""):
        return self.s3.list_objects_v2(Bucket=self.bucket_name,
                                        Prefix= prefix)

    def download_single_CUR_data(self, report_key, file_name):
        """
        Download CUR data from S3
        """
        # Create folder to download CUR data
        download_folder_path = self.get_download_path(self.storage_id)
        self.make_download_temp_dir(self.storage_id)

        download_file_path = os.path.join(download_folder_path, file_name)

        self.s3.download_file(
                Bucket = self.bucket_name,
                Key = report_key,
                Filename = download_file_path
            )

        return download_file_path


    def download_CUR_data(self, bucket_name, report_name, report_prefix):
        """
        Download CUR data from S3
        """
        # Create folder to download CUR data
        download_folder_path = self.get_download_path(self.account_id)
        self.make_download_temp_dir(self.storage_id)

        download_obj_list = []
        # Get objects list
        try:
            objects = self.s3.list_objects(
                Bucket=bucket_name,
                Prefix=report_prefix)
            for content in objects['Contents']:
                object_path = content['Key']
                if os.path.split(object_path)[1].split('.')[-1] == 'gz':
                    download_obj_list.append(object_path)
        except Exception as e:
            traceback.print_exc()
            logger.error(f'Error during get objects list from S3 - {e}')
            raise Exception from e

        downloaded_files_path = []
        # Download contents from s3
        for content in download_obj_list:
            download_file_path = os.path.join(download_folder_path, content.replace('/', '&&'))
            self.s3.download_file(
                Bucket = bucket_name,
                Key = content,
                Filename = download_file_path
            )
            downloaded_files_path.append(download_file_path)

        # Return downloaded files list
        return downloaded_files_path

    def upload_CUR_data(self, file_path):
        """
        Upload CUR data to S3
        """
        # TODO use the instance's bucket_name
        bucket_name = "grumatic-dev-pandas"
        try:

            object_key = file_path[file_path.rfind('/')+1:]
            object_key = object_key.replace('&&', '/')

            self.s3.upload_file(file_path, bucket_name, object_key)
            print(f"Uploading key: {object_key}")
        except Exception as e:
            logger.error(f'Error during upload CUR data to S3 - {e} - {bucket_name} - {file_path}')
            raise Exception

    def get_download_path(self, account_id):
        return "{temp_path}/{account_id}".format(
                            temp_path = configure.DOWNLOAD_PATH, 
                            account_id = account_id)

    def make_download_temp_dir(self, account_id):
        """
        Create download folder
        """
        download_path = self.get_download_path(account_id)

        # Create directory if download path does not exist
        if(not(os.path.isdir(download_path) and os.path.exists(download_path))):
            try:
                os.makedirs(download_path)
            except OSError:
                logger.error(f"Creation of the directory {download_path} failed")
                raise Exception("Creation of the directory {} failed" % download_path)
            logger.info("Successfully created the directory %s" % download_path)

        return True

    def remove_download_temp_dir(self):
        download_path = configure.DOWNLOAD_PATH

        # Remove temp folder
        if os.path.isdir(download_path) and os.path.exists(download_path):
            try:
                shutil.rmtree(download_path)
            except OSError:
                logger.info("Deletion of the directory %s failed" % download_path)
                raise Exception("Deletion of the directory {} failed" % download_path)
            logger.info("Successfully deleted the directory %s" % download_path)

        return True