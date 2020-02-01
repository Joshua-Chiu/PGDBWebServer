from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import include
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    # path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url('^', include('django.contrib.auth.urls')),
]
