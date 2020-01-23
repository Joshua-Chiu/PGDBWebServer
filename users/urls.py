from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('personalisation', views.personalisation, name='personalisation'),
    path('personalisation/submit', views.personalisation_submit, name='personalisation_submit'),
    path('autofocus/<int:num>', views.autofocus_submit, name='autofocus'),
]
