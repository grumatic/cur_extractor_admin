from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from accounts.forms import (AccountForm,
                            CredentialForm,
                            CompanyForm,
                            ReportInfoForm,
                            StorageInfoForm

                            )
from accounts.models import (Account,
                            Company,
                            Credential,
                            ReportInfo,
                            StorageInfo
                            )


def index(request):
    # template = loader.get_template('template/admin/base.html')

    return HttpResponse(render(request, 'layout/base2.html', None))

def dashboard_view(request):
    # template = loader.get_template('template/admin/base.html')

    return HttpResponse(render(request, 'content/dashboard.html', None))

def account_view(request, account_id: int= None):
    query = {'account_id': account_id} if account_id else {}
    accounts = Account.objects.filter(**query)

    context = {
        'accounts': accounts
        }
    return HttpResponse(render(request, 'content/view-accounts.html', context))

def company_view(request, company_id: int=None):
    query = {'id': company_id} if company_id else {}
    comps = Company.objects.filter(**query)

    context = {
        'companies': comps
        }
    return HttpResponse(render(request, 'content/view-companies.html', context))

def credential_view(request, credential_id: int=None):
    query = {'id': credential_id} if credential_id else {}
    credentials = Credential.objects.filter(**query)

    context = {
        'credentials': credentials
        }
    return HttpResponse(render(request, 'content/view-credentials.html', context))

def report_info_view(request, report_info_id: int=None):
    query = {'id': report_info_id} if report_info_id else {}
    report_infos = ReportInfo.objects.filter(**query)

    context = {
        'report_infos': report_infos
        }
    return HttpResponse(render(request, 'content/view-report-infos.html', context))

def storage_info_view(request, storage_info_id: int=None):
    query = {'id': storage_info_id} if storage_info_id else {}
    storage_infos = StorageInfo.objects.filter(**query)

    context = {
        'storage_infos': storage_infos
        }
    return HttpResponse(render(request, 'content/view-storage-infos.html', context))








################################################################
########################  Create Views  ########################
################################################################
def create_account(request):
    form = AccountForm(request.POST)
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        return redirect('/dashboard')

    context = {'form': form}
    return render(request, 'content/create-company.html', context)

def create_credential(request):
    form = CredentialForm()
    if request.method == 'POST':
        form = CredentialForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/dashboard')

    context = {'form': form}
    return render(request, 'content/create-company.html', context)

def create_company(request):
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/dashboard')

    context = {'form': form}
    return render(request, 'content/create-company.html', context)

def create_report_info(request):
    form = ReportInfoForm()
    if request.method == 'POST':
        form = ReportInfoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/dashboard')

    context = {'form': form}
    return render(request, 'content/create-company.html', context)

def create_storage_info(request):
    form = StorageInfoForm()
    if request.method == 'POST':
        form = StorageInfoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/dashboard')

    context = {'form': form}
    return render(request, 'content/create-company.html', context)
