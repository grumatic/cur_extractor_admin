from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # View
    path('dashboard/', views.dashboard_view, name='view_dashboard'),
    path('company/', views.company_view, name='view_company'),
    path('company/<int:company_id>/', views.company_view, name='view_company'),
    path('account/', views.account_view, name='view_account'),
    path('account/<int:account_id>/', views.account_view, name='view_account'),
    path('credential/', views.credential_view, name='view_credential'),
    path('credential/<int:account_id>/', views.credential_view, name='view_credential'),
    path('report-info/', views.report_info_view, name='view_report-info'),
    path('report-info/<int:account_id>/', views.report_info_view, name='view_report-info'),
    path('storage-info/', views.storage_info_view, name='view_storage-info'),
    path('storage-info/<int:storage_info_id>/', views.storage_info_view, name='view_storage-info'),
    
    # Create
    # path('company', views.create_company_view, name='index'),
    path('create-account/', views.create_account, name='create_account'),
    path('create-credential/', views.create_credential, name='create_credential'),
    path('create-company/', views.create_company, name='create_company'),
    path('create-report-info/', views.create_report_info, name='create_report-info'),
    path('create-storage-info/', views.create_storage_info, name='create_storage-info'),

]