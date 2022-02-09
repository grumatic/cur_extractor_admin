from django.db import models

from accounts.utils import accept_exactly_one


class StorageInfo(models.Model):
    bucket_name = models.CharField(max_length=63)
    prefix = models.CharField(max_length=1000, blank=True)
    access_key = models.CharField(max_length=128)
    secret_key = models.CharField(max_length=1024)

    class Meta:
        db_table = "storage_info"


class PayerAccount(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    storage_info = models.ForeignKey(StorageInfo, on_delete=models.CASCADE)
    class Meta:
        db_table = "payer"

    @property
    def accounts(self):
        return list(LinkedAccount.objects.filter(payer=self.id))

    @classmethod
    def get_by_storage_info(cls, storage_info):
        return cls.objects.filter(storage_info=storage_info)

class LinkedAccount(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    payer = models.ForeignKey(PayerAccount, on_delete=models.CASCADE)
    class Meta:
        db_table = "account"

    @classmethod
    def get_by_report_info(cls, report_info):
        return cls.objects.filter(reportinfo=report_info)

class ReportInfo(models.Model):
    name = models.CharField(max_length=32)
    prefix = models.CharField(max_length=128)
    payer = models.ForeignKey(PayerAccount, on_delete=models.CASCADE)
    accounts = models.ManyToManyField(
                            LinkedAccount,
                            blank=True)
    access_key = models.CharField(max_length=128) #TODO add min_length
    secret_key = models.CharField(max_length=1024)
    bucket_name = models.CharField(max_length=63) #TODO add min_length


    class Meta:
        db_table = "report_info"

    # def save(self, *args, **kwargs):
    #     print(args)
    #     print(kwargs)

    # def get_linked_accounts(self):
    #     return [account.account_id for account in self.accounts]


