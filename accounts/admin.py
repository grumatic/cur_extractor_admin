from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import (Account,
                    Company,
                    Credential,
                    ReportInfo,
                    StorageInfo)

admin.site.unregister(Group)
admin.site.unregister(User)


admin.site.register(Account)
admin.site.register(Company)
admin.site.register(Credential)
admin.site.register(ReportInfo)
admin.site.register(StorageInfo)
