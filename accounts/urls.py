from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # View
    path('', views.storage_info_view, name='storage_info'),
    path('payer-account/', views.payer_account_view, name='view_company'),
    path('payer-account/<int:payer_id>/', views.payer_account_view, name='view_company'),
    path('account/', views.linked_account_view, name='view_account'),
    path('account/<int:account_id>/', views.linked_account_view, name='view_account'),
    path('report-info/', views.report_info_view, name='view_report-info'),
    path('report-info/<int:account_id>/', views.report_info_view, name='view_report-info'),
    path('storage-info/', views.storage_info_view, name='view_storage-info'),
    path('storage-info/<int:account_id>/', views.storage_info_view, name='view_storage-info'),
    
    # Delete
    path('delete-storage-info/<int:storage_info_id>/', views.delete_storage_info, name='delete_storage-info'),
    path('delete-payer-account/<int:payer_account_id>/', views.delete_payer_account, name='delete_payer-account'),
    path('delete-linked-account/<int:linked_account_id>/', views.delete_linked_account, name='delete_linked-account'),
    path('delete-report-info/<int:report_info_id>/', views.delete_report_info, name='delete_report-info'),
    
    # Create
    # path('PayerAccount', views.create_company_view, name='index'),
    path('create-linked-account/', views.create_account, name='create_account'),
    path('create-payer-account/', views.create_company, name='create_company'),
    path('create-report-info/', views.create_report_info, name='create_report-info'),
    path('create-storage-info/', views.create_storage_info, name='create_storage-info'),

    # # CUR
    path('cur/start_hardcoded/', views.cur_hardcoded, name="cur_hardcoded")

]