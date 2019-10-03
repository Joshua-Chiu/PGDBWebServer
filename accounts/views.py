from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import generic
from django.template.loader import get_template
from django.core.mail import send_mail
from django.conf import settings


def index(request):
    return HttpResponseRedirect('/')


