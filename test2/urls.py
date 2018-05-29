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
    path('settings/codes/submit', views.codes_submit, name='codes_submit'),
]
