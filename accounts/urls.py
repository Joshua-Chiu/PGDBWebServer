from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import include
from django.conf.urls import url
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    url('^', include('django.contrib.auth.urls')),
]
