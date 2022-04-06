import json
import logging.config
import os
from pprint import pprint
import sys
import traceback


from cur_extractor.celery import app

from accounts.models import (LinkedAccount,
                            PayerAccount,
                            ReportInfo,
                            StorageInfo)



from cur_extractor.Config import Config as configure
from cur.s3_handler import S3HandlerClass
from cur.extractor import (extract_chunk, extract_data)
from cur.models import CURReport

logging.config.fileConfig(fname='cur_extractor/Config/logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)



def needs_update(report_obj, storage_id):
    """
    Returns whether the report needs to be updated
    """
    try:
        report_manifest = CURReport.get_by_storage_and_key(
            storage_id=storage_id,
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
        if obj.key.endswith("Manifest.json") and needs_update(obj,s3_downloader.storage_id):
            body = s3_downloader.get_object_as_json(key=obj.key)
            changed_reports.append(
                    {
                        "manifest_key": obj.key,
                        "report_keys": body["reportKeys"],
                        "last_updated": obj.last_modified
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


def update_report(downloaded_path, report_infos, s3_downloader, report, storage_info):
    """
    Iterate through the report_infos, extract data updating.
    """
    for report_info in report_infos:
        logger.info(f"Updating {report['manifest_key']} with report Output CUR Info '{report_info.name}'")
        accounts = LinkedAccount.get_by_report_info(report_info)
        account_ids = [account.account_id for account in accounts]

        output_folder = f"{downloaded_path[:downloaded_path.rfind('/')+1]}{report_info.id}/"
        output_folder = s3_downloader.make_temp_dir(output_folder)
        path_key = f"{configure.DEFAULT_PREFIX}&&{downloaded_path.split('&&')[-2]}&&{downloaded_path.split('&&')[-1]}"
        new_key = f"{report['manifest_key'][:report['manifest_key'].rfind('/')]}"
        new_key = f"{new_key}/{downloaded_path.split('&&')[-1]}"

        upload_path = f"{output_folder}{path_key}"
        
        if upload_path[upload_path.rfind('.'):] != ".gz":
            upload_path = f"{upload_path[:upload_path.rfind('.')]}.gz"

        if new_key[new_key.rfind('.'):] != ".gz":
            new_key = f"{new_key[:new_key.rfind('.')]}.gz"


        logger.info(f"Extracting data for Output CUR Info '{report_info.name}' [Target-{new_key}]")
        is_extracted = extract_data(downloaded_path, upload_path, report_info, account_ids)

        if not is_extracted:
            continue
        s3_uploader = S3HandlerClass(
                            arn=report_info.arn,
                            storage_id= report_info.id,
                            bucket_name= report_info.bucket_name,
                            external_id=report_info.external_id,
                        )

        logger.info(f"Uploading {new_key}")
        s3_uploader.upload_CUR_data(file_path=upload_path, key=new_key)


        cur_track = CURReport.get_by_report_and_key(
            report_info=report_info,
            manifest_key=report["manifest_key"]
        )
        if cur_track:
            cur_track.last_updated = report["last_updated"]
        else:
            cur_track = CURReport(
                storage_info=storage_info,
                report_info=report_info,
                manifest_key=report["manifest_key"],
                last_updated=report["last_updated"]
            )
        cur_track.save()

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
            bucket_name= storage_info.bucket_name,
            external_id=storage_info.external_id,
        )

        logger.info(f"Checking report changes in Original CUR Info '{storage_info.name}'")
        # Get changed reports
        changed_reports = get_changed_reports(
            s3_downloader= s3_downloader,
            prefix= storage_info.prefix
        )

        report_infos = get_report_infos(storage_info)
        logger.info(
            f"Reports to be updated from original CUR Info '{storage_info.name}': \
{[report['manifest_key'] for report in changed_reports]}"
        )

        for report in changed_reports:
            # Download Changed Files
            downloaded_paths = []
            logger.info("Downloading objects from report...")
            downloaded_paths += download_keys(
                keys=report["report_keys"],
                s3_downloader=s3_downloader
            )

            # Go through the reports
            for downloaded_path in downloaded_paths:
                # Extract data per report & upload it
                update_report(
                    downloaded_path,
                    report_infos,
                    s3_downloader,
                    report,
                    storage_info
                )


        # Delete the temp folder
        if configure.NEED_REMOVE_TEMP:
            logger.info(f"Remove temp folder for original CUR Info '{storage_info.name}'")
            s3_downloader.remove_download_temp_dir()
