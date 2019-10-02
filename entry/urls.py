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
    path('scholar_submit', views.scholar_submit, name='scholar_submit'),
    path('error', views.error, name='error'),
    path('dictionary/<slug:point_catagory>', views.dictionary, name='dictionary'),
    path('upload_file/<slug:point_catagory>', views.upload_file, name='upload_file'),
    path('point_submit/<slug:point_catagory>', views.point_submit, name='point_submit'),
    path('ajax/validate_student_name/', views.validate_student_name, name='validate_student_name'),
    path('ajax/validate_point_code/', views.validate_point_code, name='validate_point_code'),
]
