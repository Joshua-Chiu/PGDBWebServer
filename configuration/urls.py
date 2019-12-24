from django.urls import path
from . import views

app_name = 'configuration'

urlpatterns = [
    path('help', views.help, name='help'),
    path('offline', views.offline, name='offline'),
]
