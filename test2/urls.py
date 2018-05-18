from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('search', views.search, name="search"),
    path('student/<int:num>', views.student_info, name="student_info"),
    path('student/<int:num>/submit', views.student_submit, name="student_submit"),
    path('settings', views.settings, name="settings"),
]
