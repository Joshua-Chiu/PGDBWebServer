from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template


def index(request):
    template = get_template('export/index.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


def printing(request):
    template = get_template('export/print.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


def export_files(request):
    template = get_template('export/files.html')
    context = {

    }
    return HttpResponse(template.render(context, request))
