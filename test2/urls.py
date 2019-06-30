from django.urls import path
from . import views

app_name = 'test2'

urlpatterns = [
    path('', views.index, name="index"),
    path('search', views.search, name="search"),
    path('student/<int:num>', views.student_info, name="student_info"),
    path('student/<int:num>/submit', views.student_submit, name="student_submit"),
    path('settings', views.settings, name="settings"),
    path('settings/codes', views.codes, name='codes'),
    path('settings/plist', views.plist, name='plist'),
    path('settings/codes/submit', views.codes_submit, name='codes_submit'),
    path('settings/plist_submit', views.plist_submit, name='plist_submit'),
    path('help', views.help, name='help'),
    path('export', views.export, name='export'),
    path('autofocus/<int:num>', views.autofocus_submit, name='autofocus'),
]
