import json
import logging.config
import os
from pprint import pprint
import sys
import traceback

import pandas as pd


from accounts.models import (Account,
                            Credential,
                            Company,
                            ReportInfo,
                            StorageInfo)



from cur_extractor.Config import Config as configure
from cur.s3_handler import S3HandlerClass
from cur.extractor import (make_tmp_folder_to_extract_result,
                            extract_data_to_csv,
                            make_folder_for_company_result,
                            create_folder)
from cur.models import CURReport
from cur.Utils.GZIPHandler import decompress_gz_file, compress_gz_file
# logging.config.fileConfig(fname='cur_extractor/Config/logger.conf', disable_existing_loggers=False)
# logger = logging.getLogger(__name__)

class Extractor:

    s3_downloader: S3HandlerClass
    s3_uploader: S3HandlerClass
    report_info: ReportInfo
    report_info: ReportInfo
    """
    Columns
    blended/unblended
    savings
    """

    def __init__(   self,
                    s3_downloader: S3HandlerClass, 
                    s3_uploader: S3HandlerClass,
                    report_info: ReportInfo
                ):
        self.s3_downloader = s3_downloader
        self.s3_uploader = s3_uploader
        self.report_info = report_info

    def start(self,):
        # Get changed reports as S3 Objects
        changed_reports = self.get_changed_reports()

        for report in changed_reports:
            self.update_info(report)

    def get_changed_reports(self):
        objects = self.s3_downloader.s3.list_objects_v2(Bucket=self.s3_downloader.bucket_name,
                                                        Prefix= "grumatic-cur/grumatic-cur/")
        # objects = self.s3_downloader.s3.list_object_versions(Bucket=self.s3_downloader.bucket_name)
        # reports = CURReport.filter_by_account(account_id=self.s3_downloader.account_id)
        changed_reports = []
        for obj in objects["Contents"]:
            if obj["Key"].endswith("Manifest.json"): # and self.updated_report(obj): 
                body = self.s3_downloader.get_object_as_json(key=obj["Key"])
                changed_reports.append(
                        {
                            "manifest_key": obj["Key"],
                            "report_keys": body["reportKeys"],
                            "last_updated": obj["LastModified"],
                        }
                    )
                break
        return changed_reports

    def updated_report(self, obj):
        try:
            report_manifest = CURReport.get_by_account_and_key(
                                                account_id=self.s3_downloader.account_id,
                                                manifest_key=obj["Key"]
                                            )
            print(report_manifest.is_report_changed(obj["LastModified"]))
            return report_manifest.is_report_changed(obj["LastModified"])
        except Exception as e:
            # TODO change to not found Exception
            return True

    def update_info(self, report):
        for report_key in report['report_keys']:
            file_name = report_key.replace('/', '&&')
            downloaded_path = self.s3_downloader.download_single_CUR_data(report_key, file_name)
            
            # Make dst path
            split_path = downloaded_path.split("/")

            split_path.insert(3,"result")
            dst_path = "/".join(split_path)
            create_folder(dst_path[:dst_path.rfind("/")])

            # Create Extracted File
            # TODO include Columns the optional trims
            self.column_trim(downloaded_path, dst_path, "identity/LineItemId", 1e5)

            self.s3_uploader.upload_CUR_data(dst_path)

        # Update db
        CURReport(account_id=Account.get_by_id(account_id=self.s3_downloader.account_id),
                manifest_key=report["manifest_key"],
                last_updated=report["last_updated"]).save()


        if configure.NEED_REMOVE_TEMP:
            # logger.info('Remove temp folder')
            self.s3_downloader.remove_download_temp_dir()



    def column_trim(self, input_file, output_file, columns, chunk_size):
        columns = columns.split(",")
        chunk_size = float(chunk_size)
        header = True
        for chunk in pd.read_csv(input_file, chunksize=chunk_size):
            chunk = chunk[columns]
            
            chunk.to_csv(output_file,
                        header=header,
                        compression='gzip',
                        mode='w' if header else 'a',
                        index=False)
            header = False

def start(access_key,
            secret_key,
            account_id,
            bucket_name,
            report_name,
            report_prefix,
            company_name
            ):
    print("Starting...")
    cur_downloader = S3HandlerClass(
        access_key = access_key,
        secret_key = secret_key,
        account_id = account_id)
    
    result_path = make_tmp_folder_to_extract_result(
        cur_downloader.get_download_path(account_id = account_id),
    )
    
    cur_downloaded_files_path = cur_downloader.download_CUR_data(
        bucket_name = bucket_name,
        report_name = report_name,
        report_prefix = report_prefix
    )

    csv_result_files = []
    gzip_target_folder_path = make_folder_for_company_result(result_path, company_name)

    # Extract CUR data
    for cur_csv_file in cur_downloaded_files_path:
        try:
            
            source_folder_path = os.path.dirname(cur_csv_file)
            dst_folder_path = os.path.join(source_folder_path, configure.RESULT_PATH)
            dst_path = cur_csv_file.replace(source_folder_path, dst_folder_path)
            column_trim(cur_csv_file, dst_path, "identity/LineItemId",100000)

        except ValueError:
            # logger.error(f'There are no content with account id - {company["Name"]} - {os.path.split(cur_csv_file)[1]}')
            continue
        csv_result_files.append(dst_path)

    # init S3 uploader
    cur_uploader = S3HandlerClass(
        access_key = access_key,
        secret_key = secret_key,
        account_id = account_id
    )
    # logger.info('Upload cur data to company\' S3')
    for upload_target in csv_result_files:
        # Upload file on S3
        print("uploading")
        try:
            cur_uploader.upload_CUR_data(
                bucket_name = "grumatic-dev-pandas",
                file_name = upload_target,
                parent_folder_path = gzip_target_folder_path)
        except Exception as e:
            continue


def run():
    print("Running extractor")
    report_info = ReportInfo.get_current_info()
    for company in Company.objects.all():

        for account in company.accounts:
            credentials = Credential.get_by_account_id(account.account_id)
            storage_infos = StorageInfo.get_by_account_id(account.account_id)

            bucket_name = storage_infos[0].bucket_name
            access_key = credentials[0].access_key
            secret_key = credentials[0].secret_key


            s3_downloader = S3HandlerClass(
                access_key=access_key,
                secret_key=secret_key,
                bucket_name=bucket_name,
                account_id=account.account_id
            )

            extractor = Extractor(
                s3_downloader=s3_downloader,
                s3_uploader=s3_downloader,
                report_info=report_info
            )

            extractor.start()
            
            print("---------")



