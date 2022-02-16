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
        # widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = ReportInfo
        fields = (
            'name',
            'prefix',
            'payer',
            'arn',
            # 'access_key',
            # 'secret_key',
            'bucket_name',
            'credit',
            'refund',
            'blended'
        )


class StorageInfoForm(forms.ModelForm):
    class Meta:
        model = StorageInfo
        fields = '__all__'


# class ReportInfo_Form(forms.Form):
#     name = forms.CharField(max_length=32)
#     prefix = forms.CharField(max_length=128)
#     # payer_id = models.ForeignKey(PayerAccount, on_delete=models.CASCADE)
#     # account_ids = models.ManyToManyField(
#     #                         LinkedAccount,
#     #                         # related_name="account",
#     #                         # null=True,
#     #                         blank=True)

#     color = forms.ModelChoiceField(queryset=PayerAccount.objects.all())
#     speed = forms.ModelChoiceField(queryset=LinkedAccount.objects.all())
#     access_key = forms.CharField(max_length=128) #TODO add min_length
#     secret_key = forms.CharField(max_length=1024)
#     bucket_name = forms.CharField(max_length=63) #TODO add min_length
