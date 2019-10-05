from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User


def index(request):
    return HttpResponseRedirect('/')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']  # get username
        password = request.POST['txtPwd']  # and password
        user = authenticate(request=request, username=username, password=password)  # checking username and pwd
        if user is not None:
            if user.is_active:
                login(request, user)
