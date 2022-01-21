from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import CompanyAccount, ReportInfo

admin.site.register(CompanyAccount)
admin.site.register(ReportInfo)
admin.site.unregister(Group)
admin.site.unregister(User)
