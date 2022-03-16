from django.urls import path

from . import views

urlpatterns = [
    path('download_updates/', views.download_updates, name='download-cur_updates'),
    path('updates/', views.view_updates, name='view-cur_updates'),
    path('updates/<int:page>/', views.view_updates, name='view-cur_updates'),
    path('updates_by_report/<int:report_info_id>/', views.view_by_report, name='view-cur_updates_by_report'),
    path('updates_by_report/<int:report_info_id>/<int:page>', views.view_by_report, name='view-cur_updates_by_report'),
]