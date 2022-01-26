from django import forms

from accounts.models import Account, ReportInfo, Company, StorageInfo, Credential


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = '__all__'

class CredentialForm(forms.ModelForm):
    class Meta:
        model = Credential
        fields = '__all__'

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

class ReportInfoForm(forms.ModelForm):
    class Meta:
        model = ReportInfo
        fields = '__all__'

class StorageInfoForm(forms.ModelForm):
    class Meta:
        model = StorageInfo
        fields = '__all__'


class Account_Form(forms.Form):
    account_id = forms.CharField(max_length=32) #TODO clean int
    company_id = forms.ModelMultipleChoiceField(queryset=Company.objects.all())

class Credential_Form(forms.Form):
    account_id = forms.ModelMultipleChoiceField(queryset=Account.objects.all())
    report_info_id = forms.ModelMultipleChoiceField(queryset=ReportInfo.objects.all())
    access_key = forms.CharField(max_length=128) #TODO add min_length
    secret_key = forms.CharField(max_length=1024)

class Company_Form(forms.Form):
    name = forms.CharField(max_length=256) #TODO clean int

class ReportInfo_Form(forms.Form):
    name = forms.CharField(max_length=32)
    prefix = forms.CharField(max_length=128)
    in_use = forms.BooleanField()

class StorageInfo_Form(forms.Form):
    account_id = forms.ModelMultipleChoiceField(queryset=Account.objects.all())
    report_info_id = forms.ModelMultipleChoiceField(queryset=ReportInfo.objects.all())
    bucket_name = forms.CharField(max_length=63) #TODO add min_length
