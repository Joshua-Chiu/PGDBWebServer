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

    year = request.GET["year"]
    grade = request.GET["grade"]
    award = request.GET["cumulative"]

    query = f"grade:{grade} award:{award}"

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
