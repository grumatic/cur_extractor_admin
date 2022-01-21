from django.db import models



class CompanyAccount(models.Model):
    account_id = models.CharField(primary_key=True, max_length=32)
    cur_bucket = models.CharField(max_length=268)

    class Meta:
        db_table = "company_account"

class ReportInfo(models.Model):
    account_id = models.IntegerField(primary_key=True)
    report_prefix = models.CharField(max_length=32)
    report_name = models.CharField(max_length=128)
    report_bucket = models.CharField(max_length=268)
    access_key = models.CharField(max_length=100)
    secret_key = models.CharField(max_length=100)

    class Meta:
        db_table = "account_credential"

    def clean(self):
        admin_accs = ReportInfo.objects
        if ( admin_accs.count() == 1 #don't allow account_id to be changed
                and admin_accs.first().account_id != self.account_id):
            print(ReportInfo.objects.count())
            raise ValueError("Cannot change main account's Account ID")


"""
From:
    Raw Data (CUR csv):
    Bucket
    Object
    AccessKey
    SecretKey


To:
    Curated Data (Filtered CUR csv):
    Bucket
    Object
    AccessKey
    SecretKey

Report:
    BucketName
"""
