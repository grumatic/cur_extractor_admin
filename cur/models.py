from django.db import models

from accounts.models import Account



class CURReport(models.Model):
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    manifest_key = models.CharField(primary_key=True, max_length=1024)
    last_updated = models.DateTimeField()

    class Meta:
        db_table = 'cur_report'
        unique_together = ('account_id', 'manifest_key',)

    @classmethod
    def get_by_account_and_key(cls, account_id, manifest_key):
        return cls.objects.get(account_id=account_id, manifest_key=manifest_key)

    def is_report_changed(self, last_updated):
        return self.last_updated != last_updated

    @classmethod
    def filter_by_account(cls, account_id):
        return cls.objects.filter(account_id=account_id)

    