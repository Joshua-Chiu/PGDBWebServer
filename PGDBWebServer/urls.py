"""PGDBWebServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views
from django.views.generic import RedirectView
from django.conf.urls import url

urlpatterns = [
    # path('', views.data, name="data_redirect"),
    path('', views.accounts, name="login"),
    path('entry/', include('entry.urls')),
    path('data/', include('data.urls')),
    path('export/', include('export.urls')),

    path('users/', include('users.urls')),
    path('configuration/', include('configuration.urls')),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/icon.png')),
    url(r'session_security/', include('session_security.urls')),
]

handler400 = 'configuration.views.handle_exception_40X'
handler403 = 'configuration.views.handle_exception_40X'
handler404 = 'configuration.views.handle_exception_40X'
handler500 = 'configuration.views.handle_exception_50X'

admin.site.site_header = "Point Grey Database Management"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Database Management Portal"
