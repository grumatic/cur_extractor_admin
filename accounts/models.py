from django.db import models

from accounts.utils import accept_exactly_one

class Company(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        db_table = "company"

    @property
    def accounts(self):
        return list(Account.objects.filter(company_id=self.id))


class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)
    class Meta:
        db_table = "account"


class ReportInfo(models.Model):
    name = models.CharField(max_length=32)
    prefix = models.CharField(max_length=128)
    in_use = models.BooleanField(default=False)

    class Meta:
        db_table = "report_info"


    def save(self, disabling=False ,*args, **kwargs):
        if not disabling and kwargs.get('in_use', False):
            used_report = ReportInfo.objects.get(in_use__in=[True])
            used_report.in_use = False
            used_report.save()

        super(ReportInfo, self).save(*args, **kwargs)

class Credential(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    report_info_id = models.ForeignKey(ReportInfo, on_delete=models.CASCADE, blank=True, null=True)
    access_key = models.CharField(max_length=128) #TODO add min_length
    secret_key = models.CharField(max_length=1024)

    class Meta:
        db_table = "credential"

    def save(self, *args, **kwargs):
        if not accept_exactly_one(accounts_id=self.account_id,
                                report_info_id=self.report_info_id):
            raise ValueError("Must set exactly one, account_id or report_info_id")
        return super(Credential, self).save(*args, **kwargs)


class StorageInfo(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE, blank=True, null=True)
    report_info_id = models.ForeignKey(ReportInfo, on_delete=models.CASCADE, blank=True, null=True)
    bucket_name = models.CharField(max_length=63) #TODO add min_length

    class Meta:
        db_table = "storage_info"

    def save(self, *args, **kwargs):
        if not accept_exactly_one(accounts_id=self.account_id,
                                report_info_id=self.report_info_id):
            raise ValueError("Must set exactly one, account_id or report_info_id")
        super(StorageInfo, self).save(*args, **kwargs)
