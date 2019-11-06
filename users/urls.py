from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('custom_css', views.custom_css, name='custom_css'),
]
