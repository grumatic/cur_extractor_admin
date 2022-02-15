from pprint import pprint

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
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


def login_view(request):
    if request.session:
        pprint(vars(request.session))
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
def linked_account_view(request, linked_account_id: int= None):
    query = {'linked_account_id': linked_account_id} if linked_account_id else {}
    linked_accounts = LinkedAccount.objects.filter(**query)
    context = {
        'linked_accounts': linked_accounts
        }
    return HttpResponse(render(request, 'content/view-linked-accounts.html', context))


@login_required(login_url='/login/')
def payer_account_view(request, payer_id: int=None):
    query = {'id': payer_id} if payer_id else {}
    comps = PayerAccount.objects.filter(**query)

    context = {
        'payer_accounts': comps
        }
    return HttpResponse(render(request, 'content/view-payer-accounts.html', context))


@login_required(login_url='/login/')
def report_info_view(request, report_info_id: int=None):
    query = {'id': report_info_id} if report_info_id else {}
    report_infos = ReportInfo.objects.filter(**query)

    context = {
        'report_infos': report_infos
        }
    return HttpResponse(render(request, 'content/view-report-infos.html', context))

@login_required(login_url='/login/')
def storage_info_view(request, storage_info_id: int=None):
    query = {'id': storage_info_id} if storage_info_id else {}
    storage_infos = StorageInfo.objects.filter(**query)

    context = {
        'storage_infos': storage_infos
        }
    return HttpResponse(render(request, 'content/view-storage-infos.html', context))

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
########################  Create Views  ########################
################################################################

@login_required(login_url='/login/')
def create_account(request):
    form = AccountForm(request.POST)
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        return redirect('/create-linked-account/')

    context = {
        'title': "Linked Account Info",
        'form': form.as_p
        }
    return render(request, 'content/create-form.html', context)

@login_required(login_url='/login/')
def create_company(request):
    form = CompanyForm()
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/create-payer-account')

    context = {
        'title': "Payer Account Info",
        'form': form.as_p
        }
    return render(request, 'content/create-form.html', context)

@login_required(login_url='/login/')
def create_report_info(request):
    form = ReportInfoForm()
    if request.method == 'POST':
        form = ReportInfoForm(request.POST)
        if form.is_valid():
            report = form.save()
            report.accounts.set(form.cleaned_data["accounts"])
        return redirect('/create-report-info')

    context = {
        'title': "Report Info",
        'form': form.as_p
        }
    return render(request, 'content/create-form.html', context)

@login_required(login_url='/login/')
def create_storage_info(request):
    # if not request.session.get('user_id', None):
    #     return redirect('login')
    form = StorageInfoForm()
    if request.method == 'POST':
        form = StorageInfoForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/create-storage-info')

    context = {
        'title': "Storage Info",
        'form': form.as_p
        }
    return render(request, 'content/create-form.html', context)


def cur_hardcoded(request):

    tasks.run()
    return redirect(request.META['HTTP_REFERER'])
