import csv
import traceback
import logging.config
import os

from cur_extractor.Config import Config as configure

# logging.config.fileConfig(fname='cur_extractor/Config/logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)



def to_drop_savings_negation(chunk):
    """
    Get dataframe tha must be dropped.
    Payer account ID != from usage account ID and the savings plan ARN belongs to the payer's account
    """
    drop_df = chunk[(chunk['lineItem/LineItemType']=="SavingsPlanNegation") & (chunk['savingsPlan/SavingsPlanARN'].notnull())]
    drop_df = drop_df[drop_df['lineItem/UsageAccountId'] != drop_df['bill/PayerAccountId']]

    if len(drop_df) == 0:
        return False, drop_df
    drop_df = drop_df[drop_df.apply(lambda x: str(x['lineItem/UsageAccountId']) in x['savingsPlan/SavingsPlanARN'], axis=1)]
    return True, chunk

def extract_chunk(chunk, report_info, account_ids):
    """
    Extract data from a dataframe chunk, according to the report.
    """
    if account_ids:
        chunk = chunk.loc[chunk['bill/PayerAccountId'].isin(account_ids)]
    line_item_type = []
    columns = chunk.columns

    result, drop_df = to_drop_savings_negation(chunk)
    if result:
        df= pd.concat([df, drop_df]).drop_duplicates(keep=False)

    if not report_info.credit:
        line_item_type.append("Credit")

    if not report_info.tax:
        line_item_type.append("Tax")

    if not report_info.refund:
        line_item_type.append("Refund")

    if not report_info.discount:
        line_item_type.extend(("EDPDiscount", "RIVolumeDiscount"))

        if "discount/RIVolumeDiscount" in columns:
            chunk["discount/RIVolumeDiscount"] = 0
        if "discount/EDPDiscount" in columns:
            chunk["discount/EDPDiscount"] = 0
        if "discount/TotalDiscount" in columns:
            chunk["discount/TotalDiscount"] = 0
        if "discount/SPPDiscount" in columns:
            chunk["discount/SPPDiscount"] = 0


    if line_item_type:
        chunk = chunk.loc[~chunk['lineItem/LineItemType'].isin(line_item_type)]

    if not report_info.blended:
        columns = chunk.columns
        if 'lineItem/UnblendedRate' in columns:
            chunk['lineItem/BlendedRate'] = chunk['lineItem/UnblendedRate']
        if 'lineItem/UnblendedCost' in columns:
            chunk['lineItem/BlendedCost'] = chunk['lineItem/UnblendedCost']
        if 'lineItem/NetUnblendedRate' in columns:
            chunk['lineItem/NetBlendedRate'] = chunk['lineItem/NetUnblendedRate']
        if 'lineItem/NetUnblendedCost' in columns:
            chunk['lineItem/NetBlendedCost'] = chunk['lineItem/NetUnblendedCost']

    return chunk



def make_tmp_folder_to_extract_result(temp_path):
    """
    Create folder to save extract result
    """
    target_path = os.path.join(temp_path, configure.RESULT_PATH)
    if not os.path.isdir(target_path):
        try:
            os.makedirs(target_path)
        except OSError:
            logger.error(f"Creation of the directory {target_path} failed")
            raise Exception("Creation of the directory {} failed" % target_path)
    logger.info("Successfully created the directory %s" % target_path)
    return target_path

def make_folder_for_company_result(path, target):
    """
    Create folder to save gzip result - under save extract result
    """
    target_path = os.path.join(path, target)
    if not os.path.isdir(target_path):
        try:
            os.makedirs(target_path)
        except Exception:
            logger.error(f"Creation of the directory {target_path} failed")
            raise Exception("Creation of the directory {} failed" % target_path)
    # logger.info("Successfully created the directory %s" % target_path)
    return target_path

def create_folder(target_path):
    """
    Create a simple folder.
    """
    if not os.path.isdir(target_path):
        try:
            os.makedirs(target_path)
        except Exception:
            logger.error(f"Creation of the directory {target_path} failed")
            raise Exception("Creation of the directory {} failed" % target_path)
    # logger.info("Successfully created the directory %s" % target_path)
    return target_path


def extract_data_to_csv(source_path, account_id):
    """
    Extract data by account ID and save as csv
    """
    # Read source file
    fd = open(source_path, 'rt')
    reader = csv.reader(fd)
    source_folder_path = os.path.dirname(source_path)
    dst_folder_path = os.path.join(source_folder_path, configure.RESULT_PATH)

    dst_path = source_path.replace(source_folder_path, dst_folder_path)
    fw = open(dst_path, 'w', newline='')
    writer = csv.writer(fw)
    
    # Extract
    index = 0
    headers = []
    has_content = False
    for row in reader:
        if index == 0:
            headers = row
        else:
            obj = {}
            for i, val in enumerate(row):
                obj[headers[i]] = val
            # Write header
            if index == 1:
                writer.writerow(obj)
            # Write row if usage account matched
            if obj["lineItem/UsageAccountId"] in account_id:
                writer.writerow(row)
                if not has_content:
                    has_content = True
        index = index + 1
    if not fd.closed:
        fd.close()
    if not fw.closed:
        fw.close()
    
    # If not any row matched, raise ValueError to skip result
    if not has_content:
        raise ValueError

    return dst_path