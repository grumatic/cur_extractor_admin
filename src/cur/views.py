import csv
import math
from pprint import pprint

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator

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

from cur_extractor.Config import Config as configure




@login_required(login_url='/login/')
def view_updates(request, page: int=None):
    page = page or 1
    reports = CURReport.view_objects()

    paginator = Paginator(reports, configure.PAGE_SIZE)

    page_range = list(paginator.page_range)
    context = {
        'selected': page,
        'previous': max(page - 1, 1),
        'next': min(page + 1, len(page_range)),
        'pages': page_range,
        'cur_updates': paginator.get_page(page),
        'current_url': 'view-cur_updates',
    }

    return HttpResponse(render(request, 'content/view-cur-updates.html', context))

@login_required(login_url='/login/')
def view_by_report(request, report_info_id: int=None, page: int=None):
    page = page or 1

    query = {'report_info__id': report_info_id} if report_info_id else {}
    reports = CURReport.view_objects(**query).order_by('-last_updated')

    paginator = Paginator(reports, configure.PAGE_SIZE)

    page_range = list(paginator.page_range)
    context = {
        'selected': page,
        'previous': max(page - 1, 1),
        'next': min(page + 1, len(page_range)),
        'report_id': report_info_id,
        'pages': list(paginator.page_range),
        'cur_updates': paginator.get_page(page),
        'current_url': 'view-cur_updates_by_report'
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
