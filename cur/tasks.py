import json
import logging.config
import os
from pprint import pprint
import sys
import traceback

import pandas as pd

from cur_extractor.celery import app

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



def needs_update(report_obj, s3_downloader):
    try:
        report_manifest = CURReport.get_by_storage_and_key(
                                            storage_id=s3_downloader.storage_id,
                                            manifest_key=report_obj["Key"]
                                        )
        return report_manifest.is_report_changed(report_obj["LastModified"])
    except Exception as e:
        # TODO change to not found Exception
        print(e)
        return True

def get_changed_reports(s3_downloader: S3HandlerClass, prefix=""):
    objects = s3_downloader.get_objects_list(prefix= prefix)
    changed_reports = []
    for obj in objects["Contents"]:
        if obj["Key"].endswith("Manifest.json") and needs_update(obj,s3_downloader):
            body = s3_downloader.get_object_as_json(key=obj["Key"])
            changed_reports.append(
                    {
                        "manifest_key": obj["Key"],
                        "report_keys": body["reportKeys"],
                        "last_updated": obj["LastModified"],
                    }
                )

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
    if account_ids:
        chunk = chunk.loc[chunk['bill/PayerAccountId'].isin(account_ids)]
    line_item_type = []
    if not report_info.credit:
        # TODO use config values
        line_item_type.append("Usage")

    if not report_info.refund:
        # TODO use config values
        line_item_type.append("Tax")

        # TODO use config values
    if line_item_type:
        chunk = chunk.loc[~chunk['lineItem/LineItemType'].isin(line_item_type)]

    if not report_info.blended:

        chunk['lineItem/BlendedRate'] = chunk['lineItem/UnblendedRate']
        chunk['lineItem/BlendedCost'] = chunk['lineItem/UnblendedCost']
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
    if not(os.path.isdir(output_folder) and os.path.exists(output_folder)):
        try:
            os.makedirs(output_folder)
        except OSError as e:
            # logger.error(f"Creation of the directory {output_folder} failed")
            raise Exception("Creation of the directory {} failed" % output_folder) from e
            # logger.info("Successfully created the directory %s" % output_folder)

    return output_folder


def update_report(downloaded_path, report_infos, s3_downloader):
    for report_info in report_infos:
        print(f"\nREPORT {report_info.id}-{report_info.name}\n")
        accounts = LinkedAccount.get_by_report_info(report_info)
        account_ids = [account.account_id for account in accounts]

        output_folder = make_ouput_folder(downloaded_path, report_info.id)
        new_key = f"{report_info.prefix.replace('/','&&')}{downloaded_path.split('&&')[-2]}&&{downloaded_path.split('&&')[-1]}"
        upload_path = f"{output_folder}{new_key}"
        extract_data(downloaded_path, upload_path, report_info, account_ids)

        s3_uploader = S3HandlerClass(
                            access_key=report_info.access_key,
                            secret_key=report_info.secret_key,
                            storage_id= report_info.id,
                            bucket_name= report_info.bucket_name
                        )

        print(upload_path)
        s3_uploader.upload_CUR_data(file_path=upload_path)


@app.task
def run():
    print("Running extractor")


    for storage_info in StorageInfo.objects.all():
        s3_downloader = S3HandlerClass(
            access_key=storage_info.access_key,
            secret_key=storage_info.secret_key,
            storage_id= storage_info.id,
            bucket_name= storage_info.bucket_name
        )

        # Get changed reports
        changed_reports = get_changed_reports(
            s3_downloader= s3_downloader,
            prefix= storage_info.prefix
        )
        
        report_infos = get_report_infos(storage_info)
        for report in changed_reports:
            # Download Changed Files
            downloaded_paths = []
            # for keys in key_sets:
            downloaded_paths += download_keys(
                keys=report["report_keys"],
                s3_downloader=s3_downloader
            )

            # Go through the reports
            for downloaded_path in downloaded_paths:
                # Extract data per report & upload it
                update_report(downloaded_path, report_infos, s3_downloader)

            CURReport(storage_info=storage_info,
                    manifest_key=report["manifest_key"],
                    last_updated=report["last_updated"]).save()

        #######################################################################################
        #######################################################################################

        # Delete the temp folder
        if configure.NEED_REMOVE_TEMP:
            # logger.info('Remove temp folder')
            s3_downloader.remove_download_temp_dir()
            print("---------")
