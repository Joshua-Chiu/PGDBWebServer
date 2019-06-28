from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from test2.models import Student
from util.queryParse import parseQuery


def index(request):
    template = get_template('export/index.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


def printing(request):
    template = get_template('export/print.html')

    query = ""

    if "grade" in request.GET and request.GET["grade"]:
        query += "grade:" + request.GET["grade"] + " "
    if "cumulative" in request.GET and request.GET["cumulative"]:
        query += "award:" + request.GET["cumulative"] + " "
    if "annual" in request.GET and request.GET["annual"]:
        query += "award:" + request.GET["annual"] + " "

    print(query)

    students = parseQuery(query)

    context = {
        'student_list': students,
    }
    return HttpResponse(template.render(context, request))


def export_files(request):
    template = get_template('export/files.html')
    context = {

    }
    return HttpResponse(template.render(context, request))
