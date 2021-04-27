from django.urls import path
from . import views

app_name = 'export'

urlpatterns = [
    path('', views.index, name="index"),
    path('print-term', views.print_term, name="print-term"),
    path('print-annual', views.print_annual, name="print-annual"),
    path('print-trophies', views.print_trophies, name="print-trophies"),
    path('print-grad', views.print_grad, name="print-grad"),
    path('print-xcheck', views.print_xcheck, name="print-xcheck"),
    path('print-cslist', views.print_cslist, name="print-cslist"),
    path('files', views.export_files, name="export_files")
]
