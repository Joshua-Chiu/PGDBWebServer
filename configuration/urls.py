from django.urls import path
from . import views

app_name = 'configuration'

urlpatterns = [
    path('help', views.help, name='help'),
    path('offline', views.offline, name='offline'),
    path('commands/integrity', views.intergrity_check, name='integrity_check'),
    path('integrity', views.integrity_report, name='integrity_report')
]
