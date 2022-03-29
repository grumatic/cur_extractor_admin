import logging
from pprint import pprint

from django.db import models

from accounts.utils import accept_exactly_one

logging.config.fileConfig(fname='cur_extractor/Config/logger.conf', disable_existing_loggers=False)
logger = logging.getLogger(__name__)

class StorageInfo(models.Model):
    name = models.CharField(max_length=63)
    bucket_name = models.CharField(max_length=63)
    prefix = models.CharField(max_length=1000, blank=True)
    arn = models.CharField(max_length=1024)
    external_id = models.CharField(max_length=256, blank=True)

    class Meta:
        db_table = "storage_info"

    def __str__(self):
        return f"{self.name}"

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
        return f"{self.name}"

    @property
    def accounts(self):
        return list(LinkedAccount.objects.filter(payer=self))

    @classmethod
    def get_by_storage_info(cls, storage_info):
        return cls.objects.filter(storage_info=storage_info)


    @classmethod
    def view_objects(cls, *args, **kwargs):
        cls.verify_and_clean()
        return cls.objects.filter(**kwargs)

    @classmethod
    def verify_and_clean(cls):
        """
        Verify that the foreign key(s) in the document has been deleted.
        """

        for payer in cls.objects.all():
            try:
                payer.storage_info.id
            except Exception as e:
                logger.info(e)
                payer.delete()

class LinkedAccount(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    payer = models.ForeignKey(PayerAccount, on_delete=models.CASCADE)


    class Meta:
        db_table = "account"


    def __str__(self):
        return f"{self.name}"

    @classmethod
    def get_by_report_info(cls, report_info):
        return cls.objects.filter(reportinfo=report_info)


    @classmethod
    def view_objects(cls, *args, **kwargs):
        cls.verify_and_clean()
        return cls.objects.filter(**kwargs)

    @classmethod
    def verify_and_clean(cls):
        """
        Verify that the foreign key(s) in the document has been deleted.
        """

        for linked in cls.objects.all():
            try:
                linked.payer.account_id
            except Exception as e:
                logger.info(e)
                linked.delete()


class ReportInfo(models.Model):
    name = models.CharField(max_length=32)
    payer = models.ForeignKey(PayerAccount, on_delete=models.CASCADE)
    accounts = models.ManyToManyField(
                            LinkedAccount,
                            blank=True)
    arn = models.CharField(max_length=1024)
    external_id = models.CharField(max_length=256, blank=True)
    bucket_name = models.CharField(max_length=63)

    credit = models.BooleanField(default=True)
    refund = models.BooleanField(default=True)
    tax = models.BooleanField(default=True)
    discount = models.BooleanField(default=True)
    blended = models.BooleanField(default=True)


    class Meta:
        db_table = "report_info"


    def __str__(self):
        return f"{self.name}"

    @property
    def list_acounts(self):
        return LinkedAccount.get_by_report_info(self.id)

    @classmethod
    def view_objects(cls, *args, **kwargs):
        cls.verify_and_clean()
        return cls.objects.filter(**kwargs)

    @classmethod
    def verify_and_clean(cls):
        """
        Verify that the foreign key(s) in the document has been deleted.
        """

        for report in cls.objects.all():
            try:
                report.payer.account_id
                for account in report.list_acounts:
                    account.account_id
            except Exception as e:
                logger.info(e)
                report.delete()
