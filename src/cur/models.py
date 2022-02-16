from django.db import models

from accounts.models import StorageInfo



class CURReport(models.Model):
    storage_info = models.ForeignKey(StorageInfo, on_delete=models.CASCADE)
    manifest_key = models.CharField(primary_key=True, max_length=1024)
    last_updated = models.DateTimeField()

    class Meta:
        db_table = 'cur_report'
        unique_together = ('storage_info', 'manifest_key',)

    @classmethod
    def get_by_storage_and_key(cls, storage_id, manifest_key):
        return cls.objects.get(storage_info=StorageInfo.objects.get(id=storage_id), manifest_key=manifest_key)


    def is_report_changed(self, last_updated):
        return self.last_updated != last_updated

    @classmethod
    def filter_by_account(cls, account_id):
        return cls.objects.filter(account_id=account_id)
