from django.urls import path
from . import views

app_name = 'export'

urlpatterns = [
    path('', views.index, name="index"),
    path('printing', views.printing, name="printing"),
    path('files', views.export_files, name="export_files")
]
