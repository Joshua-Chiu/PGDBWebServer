from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('search/<int:num>', views.search, name="question"),
    path('student/<int:num>', views.student_info, name="student_info"),
    ]
