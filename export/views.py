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
        if "year" in request.GET and request.GET["year"]:
            query += "grade_" + request.GET["grade"] + "_year:" + request.GET["year"] + " "
        else:
            query += "grade:" + request.GET["grade"] + " "
    if "cumulative" in request.GET and request.GET["cumulative"]:
        if "year" in request.GET and request.GET["year"]:
            query += "award_" + request.GET["grade"] + ":" + request.GET["cumulative"] + " "
        else:
            query += "award" + ":" + request.GET["cumulative"] + " "
    if "annual" in request.GET and request.GET["annual"]:
        query += "annual_cert:" + request.GET["annual"] + "_" + request.GET["grade"] + " "

    students = parseQuery(query)

    awards_dict = {
        ":": " ",
        "_": " ",
        "annual cert": "annual",
        "grade": "gr",
        "award": "",
        "year": "",

    }
    for key, value in awards_dict.items():
        query = query.replace(key, value)


    print(query)

    context = {
        'student_list': students,
        'type': query.title()
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

    grade = int(request.GET.get("grade") or "0")
    award_type = request.GET.get("type")

    if "year" in request.GET and request.GET["year"]:
        query += "grade_" + str(grade) + "_year:" + request.GET["year"] + " "
    else:
        query += "grade:" + str(grade) + " "

    students = parseQuery(query)

    print(students[:10])

    # filter out students with no points of the right type
    new_students = students
    for s in students:
        if len(s.grade_set.get(grade=grade).points_set.filter(type__catagory=award_type)) == 0:
            new_students = new_students.exclude(id=s.id)
    students = new_students

    context = {
        'student_list': students,
        'grade_num': grade,
        'award_type': award_type,
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
