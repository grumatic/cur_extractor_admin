from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import (LinkedAccount,
                    PayerAccount,
                    ReportInfo)

admin.site.unregister(Group)
admin.site.unregister(User)


admin.site.register(LinkedAccount)
admin.site.register(PayerAccount)
admin.site.register(ReportInfo)
