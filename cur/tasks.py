import json
import logging.config
import os
from pprint import pprint
import sys
import traceback

import pandas as pd


from accounts.models import (LinkedAccount,
                            PayerAccount,
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
    """
    Columns
    blended/unblended
    savings
    """

    def __init__(   self,
                    report_infos,
                    s3_downloader: S3HandlerClass, 
                    s3_uploader: S3HandlerClass,
                ):
        self.s3_downloader = s3_downloader
        self.s3_uploader = s3_uploader
        self.report_infos = report_infos

    def start(self,):
        # Get changed reports as S3 Objects
        changed_reports = self.get_changed_reports()

        for report in changed_reports:
            self.update_info(report)

    def needs_update(self, obj):
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
            for report_info in self.report_infos:
                # Make dst path
                split_path = downloaded_path.split("/")

                split_path[3] = f"{report_info.prefix}-{split_path[3]}"
                split_path.insert(3,"result")
                dst_path = "/".join(split_path)
                create_folder(dst_path[:dst_path.rfind("/")])

                # Create Extracted File
                # TODO include Columns the optional trims
                self.column_trim(downloaded_path, dst_path, "identity/LineItemId", 1e5)

                self.s3_uploader.upload_CUR_data(dst_path)

        # Update db
        CURReport(account_id=LinkedAccount.get_by_id(account_id=self.s3_downloader.account_id),
                manifest_key=report["manifest_key"],
                last_updated=report["last_updated"]).save()



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


def get_changed_reports(s3_downloader: S3HandlerClass, prefix=""):
    objects = s3_downloader.get_objects_list(prefix= prefix)
    changed_reports = []
    for obj in objects["Contents"]:
        if obj["Key"].endswith("Manifest.json"): # and self.needs_update(obj): 
            body = s3_downloader.get_object_as_json(key=obj["Key"])
            changed_reports.append(
                    {
                        "manifest_key": obj["Key"],
                        "report_keys": body["reportKeys"],
                        "last_updated": obj["LastModified"],
                    }
                )
            break
    return changed_reports


def download_keys(keys, s3_downloader: S3HandlerClass):
    downloaded_paths = []
    for key in keys:
        file_name = key.replace('/', '&&')
        downloaded_path = s3_downloader.download_single_CUR_data(key, file_name)
        downloaded_paths.append(downloaded_path)

    return downloaded_paths

def get_report_infos(storage_info):
    payers = PayerAccount.get_by_storage_info(storage_info)
    return ReportInfo.objects.filter(payer__in=list(payers))

def extract_chunk(chunk, report_info, account_ids):
    chunk = chunk.loc[chunk['bill/PayerAccountId'].isin(account_ids)]
    return chunk

def extract_data(input_file, output_file, report_info, account_ids):
    chunk_size = 1e5
    header = True
    for chunk in pd.read_csv(input_file, chunksize=chunk_size):
        chunk = extract_chunk(chunk, report_info, account_ids)
        chunk.to_csv(output_file,
                    header=header,
                    compression='gzip',
                    mode='w' if header else 'a',
                    index=False)
        header = False


def make_ouput_folder(download_path, folder_name):
    output_folder = f"{download_path[:download_path.rfind('/')+1]}{folder_name}/"
    if(not(os.path.isdir(output_folder) and os.path.exists(output_folder))):
        try:
            os.makedirs(output_folder)
        except OSError:
            # logger.error(f"Creation of the directory {output_folder} failed")
            raise Exception("Creation of the directory {} failed" % output_folder)
        # logger.info("Successfully created the directory %s" % output_folder)

    return output_folder

def update_report(downloaded_path, report_infos):
    for report_info in report_infos:
        accounts = LinkedAccount.get_by_report_info(report_info)
        account_ids = [account.account_id for account in accounts]

        output_folder = make_ouput_folder(downloaded_path, report_info.id)
        new_key = f"{report_info.prefix.replace('/','&&')}{downloaded_path.split('&&')[-1]}"
        upload_path = f"{output_folder}{new_key}"
        extract_data(downloaded_path, upload_path, report_info, account_ids)

        s3_uploader = S3HandlerClass(
                            access_key=report_info.access_key,
                            secret_key=report_info.secret_key,
                            storage_id= report_info.id,
                            bucket_name= report_info.bucket_name
                        )

        s3_uploader.upload_CUR_data(file_path=upload_path)

        
def run():
    print("Running extractor")


    for storage_info in StorageInfo.objects.all():
        s3_downloader = S3HandlerClass(
            access_key=storage_info.access_key,
            secret_key=storage_info.secret_key,
            storage_id= storage_info.id,
            bucket_name= storage_info.bucket_name
        )

        # Get Changed Files
        changed_reports = get_changed_reports(s3_downloader= s3_downloader, prefix= storage_info.prefix)
        key_sets = [report["report_keys"] for report in changed_reports]
        # Download Changed Files
        downloaded_paths = []
        for keys in key_sets:
            downloaded_paths += download_keys(keys=keys, s3_downloader=s3_downloader) 
        

        # Go through the reports
        report_infos = get_report_infos(storage_info)
        for downloaded_path in downloaded_paths:
            # Extract data per report & upload it
            update_report(downloaded_path, report_infos)


        #######################################################################################
        #######################################################################################


        # Delete the temp folder
        if configure.NEED_REMOVE_TEMP:
            # logger.info('Remove temp folder')
            # s3_downloader.remove_download_temp_dir()
            print("---------")






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
            # logger.error(f'There are no content with account id - {PayerAccount["Name"]} - {os.path.split(cur_csv_file)[1]}')
            continue
        csv_result_files.append(dst_path)

    # init S3 uploader
    cur_uploader = S3HandlerClass(
        access_key = access_key,
        secret_key = secret_key,
        account_id = account_id
    )
    # logger.info('Upload cur data to PayerAccount\' S3')
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


