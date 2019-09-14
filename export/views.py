from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from data.models import Student
from util.queryParse import parseQuery


def index(request):
    template = get_template('export/index.html')
    context = {
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def print_annual(request):
    template = get_template('export/print-annual.html')

    query = ""

    if "grade" in request.GET and request.GET["grade"]:
        query += "grade:" + request.GET["grade"] + " "
    if "cumulative" in request.GET and request.GET["cumulative"]:
        query += "award:" + request.GET["cumulative"] + " "
    if "annual" in request.GET and request.GET["annual"]:
        query += "annual_cert:" + request.GET["annual"] + "_" + request.GET["grade"] + " "

    print(query)

    students = parseQuery(query)

    context = {
        'student_list': students,
        'type': query.replace(':', ' ').replace("award ", "").title(),
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def print_grad(request):
    template = get_template('export/print-grad.html')

    query = ""
    students = parseQuery(query)

    context = {
        'student_list': students[:20],
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def print_xcheck(request):
    template = get_template('export/print-xcheck.html')

    query = ""
    students = parseQuery(query)

    context = {
        'student_list': students,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def export_files(request):
    template = get_template('export/files.html')
    context = {

    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')
