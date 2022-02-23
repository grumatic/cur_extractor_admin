import csv
from pprint import pprint

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect

from accounts.models import (LinkedAccount,
                            PayerAccount,
                            ReportInfo,
                            StorageInfo,
                            )

from cur.models import (CURReport)

from cur import tasks




@login_required(login_url='/login/')
def view_updates(request, cur_update_id: int=None):
    query = {'id': cur_update_id} if cur_update_id else {}
    reports = CURReport.view_objects(**query).order_by('-last_updated')[:100]

    context = {
        'cur_updates': reports
        }
    return HttpResponse(render(request, 'content/view-cur-updates.html', context))

@login_required(login_url='/login/')
def view_by_report(request, report_info_id: int=None):
    query = {'report_info__id': report_info_id} if report_info_id else {}
    reports = CURReport.view_objects(**query).order_by('-last_updated')[:100]

    context = {
        'cur_updates': reports
        }
    return HttpResponse(render(request, 'content/view-cur-updates.html', context))


@login_required(login_url='/login/')
def download_updates(request):
    reports = CURReport.view_objects().order_by('last_updated')

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="CUR-updates.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['ID', 'Last Updated', 'Storage', 'Report', 'Manifest Key'])
    for report in reports:
        writer.writerow([
            report.id,
            report.last_updated,
            report.storage_info,
            report.report_info,
            report.date_str
        ])
        
    return response
