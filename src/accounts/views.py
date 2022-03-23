from pprint import pprint

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator

from django.http import HttpResponse, JsonResponse
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

from cur_extractor.Config import Config as configure


def get_transformed_range(paginator):
    result = []

    page_range = list(paginator.page_range)

    if len(page_range) > 7:
        result = page_range[:3]
        result.append('...')
        result += page_range[len(page_range)-3:]
    else:
        result = page_range
    return result


def health_check(request):
    return JsonResponse({"health":"OK"})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            # request.session['user_id'] = user.id
        return redirect('storage_info')

    return HttpResponse(render(request, 'content/login.html', None))

def logout_view(request):
    logout(request)
    return HttpResponse(render(request, 'content/login.html', None))



@login_required(login_url='/login/')
def storage_info_view(request, page: int=None):
    page = page or 1
    # query = {'id': storage_info_id} if storage_info_id else {}
    storage_infos = StorageInfo.objects.filter()
    paginator = Paginator(storage_infos, configure.PAGE_SIZE)
    
    form = StorageInfoForm()
    if request.method == 'POST':
        form = StorageInfoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/storage-info')

    page_range = get_transformed_range(paginator)
    context = {
        'selected': page,
        'previous': max(page - 1, 1),
        'next': min(page + 1, len(page_range)),
        'pages': page_range,
        'storage_infos': paginator.get_page(page),
        'current_url': 'view-cur_updates',
        'form': form,
    }

    return HttpResponse(render(request, 'content/view-storage-infos.html', context))


@login_required(login_url='/login/')
def payer_account_view(request, page: int=None):
    page = page or 1
    # query = {'id': payer_id} if payer_id else {}
    comps = PayerAccount.view_objects()
    paginator = Paginator(comps, configure.PAGE_SIZE)
        
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/payer-account')

    page_range = get_transformed_range(paginator)
    context = {
        'selected': page,
        'previous': max(page - 1, 1),
        'next': min(page + 1, len(page_range)),
        'pages': page_range,
        'payer_accounts': paginator.get_page(page),
        'current_url': 'view-cur_updates',
        'form': form,
    }
    return HttpResponse(render(request, 'content/view-payer-accounts.html', context))


@login_required(login_url='/login/')
def linked_account_view(request, page: int= None):
    page = page or 1
    # query = {'linked_account_id': linked_account_id} if linked_account_id else {}
    linked_accounts = LinkedAccount.view_objects()
    paginator = Paginator(linked_accounts, configure.PAGE_SIZE)

    form = AccountForm()
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/account')

    page_range = get_transformed_range(paginator)
    context = {
        'selected': page,
        'previous': max(page - 1, 1),
        'next': min(page + 1, len(page_range)),
        'pages': page_range,
        'linked_accounts': paginator.get_page(page),
        'current_url': 'view-cur_updates',
        'form': form,
    }
    return HttpResponse(render(request, 'content/view-linked-accounts.html', context))


@login_required(login_url='/login/')
def report_info_view(request, page: int=None):
    page = page or 1

    report_infos = ReportInfo.view_objects()
    paginator = Paginator(report_infos, configure.PAGE_SIZE)

    form = ReportInfoForm()
    if request.method == 'POST':
        form = ReportInfoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/report-info')

    page_range = get_transformed_range(paginator)
    context = {
        'selected': page,
        'previous': max(page - 1, 1),
        'next': min(page + 1, len(page_range)),
        'pages': page_range,
        'report_infos': paginator.get_page(page),
        'current_url': 'view-cur_updates',
        'form': form,
    }

    return HttpResponse(render(request, 'content/view-report-infos.html', context))


################################################################
######################### DELETE VIEW ##########################
################################################################

@login_required(login_url='/login/')
def delete_storage_info(request, storage_info_id: int=None):
    obj = StorageInfo.objects.get(id = storage_info_id)
    obj.delete()
    return redirect('/storage-info/')

@login_required(login_url='/login/')
def delete_payer_account(request, payer_account_id: int):
    obj = PayerAccount.objects.get(account_id = payer_account_id)
    obj.delete()
    return redirect('/payer-account/')

@login_required(login_url='/login/')
def delete_linked_account(request, linked_account_id: int):
    obj = LinkedAccount.objects.get(account_id = linked_account_id)
    obj.delete()
    return redirect('/account/')

@login_required(login_url='/login/')
def delete_report_info(request, report_info_id: int):
    obj = ReportInfo.objects.get(id = report_info_id)
    obj.delete()
    return redirect('/report-info/')


################################################################
#########################  Hardcoded  ##########################
################################################################





def cur_hardcoded(request):
    
    tasks.run()
    return redirect('storage_info')

def cur_task(request):
    
    tasks.run.delay()
    return redirect('storage_info')

def cur_models(request):

    if len(StorageInfo.objects.all()) <1:
        print("StorageInfo")
        StorageInfo(
            name= "test_storage_name",
            bucket_name= "grumatic-dev",
            prefix= "grumatic-cur",
            arn= "arn:aws:iam::328341376253:role/cur-pandas-read-role"
        ).save()
    if len(PayerAccount.objects.all()) <1:
        print("PayerAccount")
        PayerAccount(
            account_id= 328341376253,
            name= "test_payer_name",
            storage_info=StorageInfo.objects.all().first()
        ).save()
    if len(LinkedAccount.objects.all()) <1:
        print("LinkedAccount")
        LinkedAccount(
            account_id= 328341376253,
            name= "test_linked_name",
            payer=PayerAccount.objects.get(account_id=328341376253)
        ).save()
    print(len(ReportInfo.objects.all()))
    if len(ReportInfo.objects.all()) <1:
        print("ReportInfo")
        rep = ReportInfo(
            name = "test_report_name",
            payer = PayerAccount.objects.get(account_id=328341376253),
            arn = "arn:aws:iam::020335907490:role/cur-writer-role",
            bucket_name = "output-cc-cur",
            credit = True,
            refund = True,
            tax = True,
            discount = True,
            blended = True
        )
        rep.save()
        rep.accounts.set(LinkedAccount.objects.filter(account_id= 328341376253))
        

    return redirect('storage_info')
