from pprint import pprint

from django.db import models

from accounts.utils import accept_exactly_one


class StorageInfo(models.Model):
    bucket_name = models.CharField(max_length=63)
    prefix = models.CharField(max_length=1000, blank=True)
    # access_key = models.CharField(max_length=128)
    arn = models.CharField(max_length=1024)

    class Meta:
        db_table = "storage_info"

    @classmethod
    def get_by_id(cls, storage_id):
        return cls.objects.get(id = storage_id)


class PayerAccount(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    storage_info = models.ForeignKey(StorageInfo, on_delete=models.CASCADE)
    class Meta:
        db_table = "payer"

    @property
    def accounts(self):
        return list(LinkedAccount.objects.filter(payer=self))

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
    arn = models.CharField(max_length=1024)
    # access_key = models.CharField(max_length=128) #TODO add min_length
    # secret_key = models.CharField(max_length=1024)
    bucket_name = models.CharField(max_length=63) #TODO add min_length

    credit = models.BooleanField(default=True)
    refund = models.BooleanField(default=True)
    blended = models.BooleanField(default=True)


    class Meta:
        db_table = "report_info"

    # def save(self, *args, **kwargs):
    #     print(args)
    #     print(kwargs)

    @property
    def list_acounts(self):
        linked_accounts = LinkedAccount.get_by_report_info(self.id)
        pprint(linked_accounts)
        return linked_accounts

    # def get_linked_accounts(self):
    #     return [account.account_id for account in self.accounts]
