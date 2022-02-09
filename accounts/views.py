from pprint import pprint

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from accounts.forms import (AccountForm,
                            CompanyForm,
                            ReportInfoForm,
                            ReportInfo_Form,
                            StorageInfoForm,
                            )
from accounts.models import (LinkedAccount,
                            PayerAccount,
                            ReportInfo,
                            )

from cur import tasks

def index(request):
    # template = loader.get_template('template/admin/base.html')

    return HttpResponse(render(request, 'layout/base.html', None))

def dashboard_view(request):
    # template = loader.get_template('template/admin/base.html')

    return HttpResponse(render(request, 'content/dashboard.html', None))

def linked_account_view(request, linked_account_id: int= None):
    query = {'linked_account_id': linked_account_id} if linked_account_id else {}
    linked_accounts = LinkedAccount.objects.filter(**query)

    context = {
        'linked_accounts': linked_accounts
        }
    return HttpResponse(render(request, 'content/view-linked-accounts.html', context))

def company_view(request, payer_id: int=None):
    query = {'id': payer_id} if payer_id else {}
    comps = PayerAccount.objects.filter(**query)

    context = {
        'companies': comps
        }
    return HttpResponse(render(request, 'content/view-payer-accounts.html', context))


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
        'report_infos': storage_infos
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

    context = {
        'form': form.as_ul()
        }
    return render(request, 'content/create-payer-account.html', context)

def create_company(request):
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/create-payer-account.html')

    context = {
        'form': form.as_ul()
        }
    return render(request, 'content/create-payer-account.html', context)

def create_report_info(request):
    form = ReportInfoForm()
    if request.method == 'POST':
        form = ReportInfoForm(request.POST)
        if form.is_valid():
            report = form.save()
            report.accounts.set(form.cleaned_data["accounts"])
        return redirect('/create-report-info')

    context = {
        'form': form.as_ul()
        }
    return render(request, 'content/create-payer-account.html', context)

def create_storage_info(request):
    form = StorageInfoForm()
    if request.method == 'POST':
        form = StorageInfoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/create-storage-info')

    context = {
        'form': form.as_ul()
        }
    return render(request, 'content/create-storage-info.html', context)




def cur_hardcoded(request):

    tasks.run()
    return redirect(request.META['HTTP_REFERER'])
