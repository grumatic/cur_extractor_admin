from pprint import pprint

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect
from accounts.forms import (AccountForm,
                            CompanyForm,
                            ReportInfoForm,
                            StorageInfoForm,
                            )
from accounts.models import (LinkedAccount,
                            PayerAccount,
                            ReportInfo,
                            StorageInfo,
                            )

from cur import tasks

def index(request):

    return HttpResponse(render(request, 'layout/base.html', None))

def login(request):
    if request.session:
        pprint(vars(request.session))
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            request.session['user_id'] = user.id
        return redirect('login')

    return HttpResponse(render(request, 'content/login.html', None))

def logout(request):
    if request.session:
        del request.session['user_id']
        return redirect('login')
    return HttpResponse(render(request, 'content/login.html', None))


def linked_account_view(request, linked_account_id: int= None):
    query = {'linked_account_id': linked_account_id} if linked_account_id else {}
    linked_accounts = LinkedAccount.objects.filter(**query)
    print(linked_accounts)
    context = {
        'linked_accounts': linked_accounts
        }
    return HttpResponse(render(request, 'content/view-linked-accounts.html', context))

def payer_account_view(request, payer_id: int=None):
    query = {'id': payer_id} if payer_id else {}
    comps = PayerAccount.objects.filter(**query)
    print(comps)

    context = {
        'payer_accounts': comps
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
        'storage_infos': storage_infos
        }
    return HttpResponse(render(request, 'content/view-storage-infos.html', context))




################################################################
########################  Create Views  ########################
################################################################
def create_account(request):
    if not request.session.get('user_id', None):
        return redirect('login')
    form = AccountForm(request.POST)
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        return redirect('/create-linked-account/')

    context = {
        'form': form.as_ul()
        }
    return render(request, 'content/create-payer-account.html', context)

def create_company(request):
    if not request.session.get('user_id', None):
        return redirect('login')
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/create-payer-account')

    context = {
        'form': form.as_ul()
        }
    return render(request, 'content/create-payer-account.html', context)

def create_report_info(request):
    if not request.session.get('user_id', None):
        return redirect('login')
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
    if not request.session.get('user_id', None):
        return redirect('login')
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
