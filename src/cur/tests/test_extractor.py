from random import random

from django.test import TestCase
import pandas as pd

from accounts.models import StorageInfo, PayerAccount, LinkedAccount, ReportInfo
from cur.extractor import extract_chunk

INPUT_DATA = {
    "bill/PayerAccountId":[
        328341376250,
        328341376251,
        328341376252,
        328341376253,
        328341376254,
        328341376255,
        328341376256,
        328341376257,
        328341376258,
        328341376259,
    ],

    "discount/RIVolumeDiscount":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "discount/EDPDiscount":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "discount/TotalDiscount":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "discount/SPPDiscount":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "lineItem/LineItemType":[
        "Credit",
        "Credit",
        "Tax",
        "Refund",
        "EDPDiscount",
        "Usage",
        "RIVolumeDiscount",
        "Usage",
        "Usage",
        "EDPDiscount"
    ],
    "lineItem/UnblendedRate":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "lineItem/BlendedRate":[
        2.45,
        2.45,
        2.45,
        2.45,
        2.45,
        2.45,
        2.45,
        2.45,
        2.45,
        2.45
    ],
    "lineItem/UnblendedCost":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "lineItem/BlendedCost":[
        23.45,
        23.45,
        23.45,
        23.45,
        23.45,
        23.45,
        23.45,
        23.45,
        23.45,
        23.45
    ],
    "lineItem/NetUnblendedRate":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "lineItem/NetBlendedRate":[
        12.45,
        12.45,
        12.45,
        12.45,
        12.45,
        12.45,
        12.45,
        12.45,
        12.45,
        12.45
    ],
    "lineItem/NetUnblendedCost":[
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45,
        123.45
    ],
    "lineItem/NetBlendedCost":[
        13.45,
        13.45,
        13.45,
        13.45,
        13.45,
        13.45,
        13.45,
        13.45,
        13.45,
        13.45
    ],
    "lineItem/UsageAccountId":[
        328341376250,
        328341376251,
        328341376252,
        328341376253,
        328341376254,
        328341376255,
        328341376256,
        328341376257,
        328341376258,
        328341376259,
    ],
    "savingsPlan/SavingsPlanARN": [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None
    ]
}

class ExtractChunkAccountTestCase(TestCase):
    def setUp(self):
        storage_info = StorageInfo(
            name= "test_storage_name",
            bucket_name= "test_in_bucket",
            prefix= "test_prefix",
            arn= "test_in_arn"
        )
        storage_info.save()

        payer = PayerAccount(
            account_id= 1234567890,
            name= "test_payer_name",
            storage_info=storage_info
        )
        payer.save()

        # linked_account = LinkedAccount(
        #     account_id= 1234567891,
        #     name= "test_linked_name",
        #     payer=payer
        # ).save()
        # linked_account = LinkedAccount(
        #     account_id= 328341376259,
        #     name= "test_linked_name",
        #     payer=payer
        # ).save()



    def test_all_allowed(self):
        """Keep the CUR unaltered"""

        report_info = ReportInfo(
            name = "test_report_name",
            payer = PayerAccount.objects.get(account_id=1234567890),
            arn = "test_out_arn",
            bucket_name = "test_out_bucket",

            credit = True,
            refund = True,
            tax = True,
            discount = True,
            blended = True
        )
        
        df_in = pd.DataFrame(INPUT_DATA)

        df_out = extract_chunk(df_in, report_info, [])

        self.assertEqual(df_in.equals(df_out), True)

    def test_filtered_missing_account_id(self):
        """Filter CUR with non existing account ids"""

        print("\n\n\n\n\n")
        ACCOUNT_DATA = {
            "bill/PayerAccountId":[
            ],
            "discount/RIVolumeDiscount":[
            ],
            "discount/EDPDiscount":[
            ],
            "discount/TotalDiscount":[
            ],
            "discount/SPPDiscount":[
            ],
            "lineItem/LineItemType":[
            ],
            "lineItem/UnblendedRate":[
            ],
            "lineItem/BlendedRate":[
            ],
            "lineItem/UnblendedCost":[
            ],
            "lineItem/BlendedCost":[
            ],
            "lineItem/NetUnblendedRate":[
            ],
            "lineItem/NetBlendedRate":[
            ],
            "lineItem/NetUnblendedCost":[
            ],
            "lineItem/NetBlendedCost":[
            ],
            "lineItem/UsageAccountId":[
            ],
            "savingsPlan/SavingsPlanARN": [
            ]
        }

        report_info = ReportInfo(
            name = "test_report_name",
            payer = PayerAccount.objects.get(account_id=1234567890),
            arn = "test_out_arn",
            bucket_name = "test_out_bucket",
            credit = True,
            refund = True,
            tax = True,
            discount = True,
            blended = True
        )
        report_info.save()
        # report_info.accounts.set(LinkedAccount.objects.filter(account_id=1234567890))
        
        df_in = pd.DataFrame(INPUT_DATA)
                
        df_out = extract_chunk(df_in, report_info, [1234567890])

        df_result = pd.DataFrame(ACCOUNT_DATA)
        print("\n\n\n\n\n")
        pd.testing.assert_frame_equal(df_result, df_out, check_dtype=False)


    def test_filtered_single_account_id(self):
        """Filter CUR with a single existing account id"""

        ACCOUNT_DATA = {
            "bill/PayerAccountId":[
                328341376259
            ],

            "discount/RIVolumeDiscount":[
                123.45
            ],
            "discount/EDPDiscount":[
                123.45
            ],
            "discount/TotalDiscount":[
                123.45
            ],
            "discount/SPPDiscount":[
                123.45
            ],
            "lineItem/LineItemType":[
                "EDPDiscount"
            ],
            "lineItem/UnblendedRate":[
                123.45
            ],
            "lineItem/BlendedRate":[
                2.45
            ],
            "lineItem/UnblendedCost":[
                123.45
            ],
            "lineItem/BlendedCost":[
                23.45
            ],
            "lineItem/NetUnblendedRate":[
                123.45
            ],
            "lineItem/NetBlendedRate":[
                12.45
            ],
            "lineItem/NetUnblendedCost":[
                123.45
            ],
            "lineItem/NetBlendedCost":[
                13.45
            ],
            "lineItem/UsageAccountId":[
                328341376259,
            ],
            "savingsPlan/SavingsPlanARN": [
                None
            ]
        }

        report_info = ReportInfo(
            name = "test_report_name",
            payer = PayerAccount.objects.get(account_id=1234567890),
            arn = "test_out_arn",
            bucket_name = "test_out_bucket",
            credit = True,
            refund = True,
            tax = True,
            discount = True,
            blended = True
        )
        report_info.save()
        
        df_in = pd.DataFrame(INPUT_DATA)
                
        df_out = extract_chunk(df_in, report_info, [328341376259])

        df_result = pd.DataFrame(ACCOUNT_DATA)

        pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_out.reset_index(drop=True), check_dtype=False)



    def test_filtered_multiple_account_id(self):
        """Filter CUR with a single existing account id"""

        ACCOUNT_DATA = {
            "bill/PayerAccountId":[
                328341376250,
                328341376259
            ],

            "discount/RIVolumeDiscount":[
                123.45,
                123.45
            ],
            "discount/EDPDiscount":[
                123.45,
                123.45
            ],
            "discount/TotalDiscount":[
                123.45,
                123.45
            ],
            "discount/SPPDiscount":[
                123.45,
                123.45
            ],
            "lineItem/LineItemType":[
                "Credit",
                "EDPDiscount"
            ],
            "lineItem/UnblendedRate":[
                123.45,
                123.45
            ],
            "lineItem/BlendedRate":[
                2.45,
                2.45
            ],
            "lineItem/UnblendedCost":[
                123.45,
                123.45
            ],
            "lineItem/BlendedCost":[
                23.45,
                23.45
            ],
            "lineItem/NetUnblendedRate":[
                123.45,
                123.45
            ],
            "lineItem/NetBlendedRate":[
                12.45,
                12.45
            ],
            "lineItem/NetUnblendedCost":[
                123.45,
                123.45
            ],
            "lineItem/NetBlendedCost":[
                13.45,
                13.45
            ],
            "lineItem/UsageAccountId":[
                328341376251,
                328341376259,
            ],
            "savingsPlan/SavingsPlanARN": [
                None,
                None
            ]
        }


        report_info = ReportInfo(
            name = "test_report_name",
            payer = PayerAccount.objects.get(account_id=1234567890),
            arn = "test_out_arn",
            bucket_name = "test_out_bucket",
            credit = True,
            refund = True,
            tax = True,
            discount = True,
            blended = True
        )
        report_info.save()
        
        df_in = pd.DataFrame(INPUT_DATA)
        df_out = extract_chunk(df_in, report_info, [328341376259, 328341376251])
        df_result = pd.DataFrame(ACCOUNT_DATA)

        pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_out.reset_index(drop=True), check_dtype=False)
