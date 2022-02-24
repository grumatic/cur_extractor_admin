from django import forms

from accounts.models import LinkedAccount, ReportInfo, PayerAccount, StorageInfo


class AccountForm(forms.ModelForm):
    class Meta:
        model = LinkedAccount
        fields = '__all__'


class CompanyForm(forms.ModelForm):
    class Meta:
        model = PayerAccount
        fields = '__all__'

class ReportInfoForm(forms.ModelForm):
    accounts = forms.ModelMultipleChoiceField(
        queryset=LinkedAccount.objects.all(),
        required=False,
        widget = forms.CheckboxSelectMultiple,
    )
    class Meta:
        model = ReportInfo
        fields = (
            'name',
            'payer',
            'arn',
            'bucket_name',
            'credit',
            'refund',
            'tax',
            'discount',
            'blended'
        )


class StorageInfoForm(forms.ModelForm):
    class Meta:
        model = StorageInfo
        fields = '__all__'


