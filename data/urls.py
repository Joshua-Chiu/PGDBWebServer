from django.urls import path
from . import views

app_name = 'data'

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

    path('archive', views.archive, name='archive'),
    path('archive_file', views.archive_file, name='archive_file'),
    path('archive_submit', views.archive_submit, name='archive_submit'),
    path('archive_wdb_submit', views.archive_wdb_submit, name='archive_wdb_submit'),

    path('personalisation', views.personalisation, name='personalisation'),
    path('personalisation/submit', views.personalisation_submit, name='personalisation_submit'),
    path('autofocus/<int:num>', views.autofocus_submit, name='autofocus'),
    path('show-all', views.show_all, name='show-all'),

    path('ajax/import_status/', views.ajax_import_status, name='ajax_import_status'),
    path('ajax/student_cumulative_data/', views.ajax_student_cumulative_data, name='ajax_student_cumulative_data'),
    path('ajax/student_points_data/', views.ajax_student_points_data, name="ajax_student_points_data"),
    path('ajax/all_points', views.ajax_all_points, name='ajax_all_points'),
]
