from django.urls import path
from . import views

app_name = 'export'

urlpatterns = [
    path('', views.index, name="index"),
    path('print-annual', views.print_annual, name="print-annual"),
    path('print-grad', views.print_grad, name="print-grad"),
    path('print-xcheck', views.print_xcheck, name="print-xcheck"),
    path('files', views.export_files, name="export_files")
]
