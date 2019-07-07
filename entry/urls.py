from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'entry'

urlpatterns = [
    path('', views.index, name="index"),
    path('service', views.service, name='service'),
    path('athletics', views.athletics, name='athletics'),
    path('fine-arts', views.fine_arts, name='fine-arts'),
    path('scholar', views.scholar, name='scholar'),
    path('error', views.error, name='error'),
    url(r'^ajax/get_student_name/$', views.get_student_name, name='get_student_name'),
]
