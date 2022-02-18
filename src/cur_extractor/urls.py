from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('accounts.urls')),
    path('cur/', include('cur.urls')),
    path('admin/', admin.site.urls),
]
