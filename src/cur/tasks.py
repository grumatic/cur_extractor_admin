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
from cur.extractor import (extract_chunk)
from cur.models import CURReport

# logging.config.fileConfig(fname='cur_extractor/Config/logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)



def needs_update(report_obj, s3_downloader):
    """
    Returns whether the report needs to be updated
    """
    try:
        report_manifest = CURReport.get_by_storage_and_key(
            storage_id=s3_downloader.storage_id,
            manifest_key=report_obj.key
        )
        return report_manifest.is_report_changed(report_obj.last_modified)
    except CURReport.DoesNotExist as e:
        return True

def get_changed_reports(s3_downloader: S3HandlerClass, prefix=""):
    """
    Return a list of details from reports that need to be updated.
    returns: [{
        "manifest_key": <str key of the report manifest>,
        "report_keys": <list of the report keys (for reports contained in multiple files)>,
        "last_updated": <datetime of the last time object was updated>
    },
    ...]
    """
    objects = s3_downloader.get_objects_list(prefix= prefix)
    changed_reports = []
    for obj in objects:
        if obj.key.endswith("Manifest.json") and needs_update(obj,s3_downloader):
            body = s3_downloader.get_object_as_json(key=obj.key)

            changed_reports.append(
                    {
                        "manifest_key": obj.key,
                        "report_keys": body["reportKeys"],
                        "last_updated": obj.last_modified,
                    }
                )
    return changed_reports

def download_keys(keys, s3_downloader: S3HandlerClass):
    """
    Prepare path and download keys.
    Return list of the downloaded paths.
    """
    downloaded_paths = []
    for key in keys:
        file_name = key.replace('/', '&&')
        downloaded_path = s3_downloader.download_single_CUR_data(key, file_name)
        downloaded_paths.append(downloaded_path)

    return downloaded_paths

def get_report_infos(storage_info):
    """
    Return a cursor with a list of the report infos associated with the given storage_info.
    """
    payers = PayerAccount.get_by_storage_info(storage_info)
    return ReportInfo.objects.filter(payer__in=list(payers))

def extract_data(input_file, output_file, report_info, account_ids):
    """
    Extract the datat from the input_file and write it to the output_file.
    """
    header = True
    for chunk in pd.read_csv(input_file, chunksize=configure.CHUNK_SIZE):
        chunk = extract_chunk(chunk, report_info, account_ids)
        chunk.to_csv(output_file,
                    header=header,
                    compression='gzip',
                    mode='w' if header else 'a',
                    index=False)
        header = False


def update_report(downloaded_path, report_infos, s3_downloader):
    """
    Iterate through the report_infos, extract data updating.
    """
    for report_info in report_infos:
        accounts = LinkedAccount.get_by_report_info(report_info)
        account_ids = [account.account_id for account in accounts]

        output_folder = f"{downloaded_path[:downloaded_path.rfind('/')+1]}{report_info.id}/"
        output_folder = s3_downloader.make_temp_dir(output_folder)
        new_key = f"{report_info.prefix.replace('/','&&')}{configure.DEFAULT_PREFIX}&&{downloaded_path.split('&&')[-2]}&&{downloaded_path.split('&&')[-1]}"
        upload_path = f"{output_folder}{new_key}"
        
        extract_data(downloaded_path, upload_path, report_info, account_ids)

        s3_uploader = S3HandlerClass(
                            arn=report_info.arn,
                            storage_id= report_info.id,
                            bucket_name= report_info.bucket_name
                        )

        s3_uploader.upload_CUR_data(file_path=upload_path)


@app.task
def run():
    """
    Task entrypoint
    """
    logger.info("Starting CUR Extractor task.")
    for storage_info in StorageInfo.objects.all():
        s3_downloader = S3HandlerClass(
            arn=storage_info.arn,
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
            downloaded_paths += download_keys(
                keys=report["report_keys"],
                s3_downloader=s3_downloader
            )

            # Go through the reports
            for downloaded_path in downloaded_paths:
                # Extract data per report & upload it
                update_report(downloaded_path, report_infos, s3_downloader)

            cur_track = CURReport(
                storage_info=storage_info,
                manifest_key=report["manifest_key"],
                last_updated=report["last_updated"]
            )
            cur_track.save()

        # Delete the temp folder
        if configure.NEED_REMOVE_TEMP:
            # logger.info('Remove temp folder')
            s3_downloader.remove_download_temp_dir()
