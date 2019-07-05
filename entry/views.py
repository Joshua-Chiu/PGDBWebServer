from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template


def checkUser(user, category):
    return user.groups.filter(name=category).exists() or user.is_superuser


def index(request):
    template = get_template('entry/index.html')
    context = {
    }
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def service(request):
    if request.user.is_authenticated and checkUser(request.user, "Service"):
        template = get_template('entry/service.html')
        context = {
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def athletics(request):
    if request.user.is_authenticated and checkUser(request.user, "Athletics"):
        template = get_template('entry/athletics.html')
        context = {
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def fine_arts(request):
    if request.user.is_authenticated and checkUser(request.user, "Fine Arts"):
        template = get_template('entry/fine-arts.html')
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def scholar(request):
    if request.user.is_authenticated and checkUser(request.user, "Scholar"):
        template = get_template('entry/scholar.html')
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def error(request):
    template = get_template('entry/error.html')
    context = {}
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/test2')
