from pprint import pprint

from django.db import models

from accounts.utils import accept_exactly_one


class StorageInfo(models.Model):
    bucket_name = models.CharField(max_length=63)
    prefix = models.CharField(max_length=1000, blank=True)
    arn = models.CharField(max_length=1024)

    class Meta:
        db_table = "storage_info"

    def __str__(self):
        return f"{self.id}- {self.bucket_name}/{self.prefix}"

    @classmethod
    def get_by_id(cls, storage_id):
        return cls.objects.get(id = storage_id)


class PayerAccount(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    storage_info = models.ForeignKey(StorageInfo, on_delete=models.CASCADE)
    class Meta:
        db_table = "payer"

    def __str__(self):
        return f"{self.name}- {self.account_id}"

    @property
    def accounts(self):
        return list(LinkedAccount.objects.filter(payer=self))

    @classmethod
    def get_by_storage_info(cls, storage_info):
        return cls.objects.filter(storage_info=storage_info)

class LinkedAccount(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    payer = models.ForeignKey(PayerAccount, on_delete=models.CASCADE)


    class Meta:
        db_table = "account"


    def __str__(self):
        return f"{self.name}- {self.account_id}"

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
    bucket_name = models.CharField(max_length=63)

    credit = models.BooleanField(default=True)
    refund = models.BooleanField(default=True)
    tax = models.BooleanField(default=True)
    discount = models.BooleanField(default=True)
    blended = models.BooleanField(default=True)


    class Meta:
        db_table = "report_info"


    def __str__(self):
        return f"{self.id} [{self.name}]- {self.bucket_name}/{self.prefix}"

    @property
    def list_acounts(self):
        return LinkedAccount.get_by_report_info(self.id)
