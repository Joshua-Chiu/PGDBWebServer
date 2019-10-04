from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from data.models import Student
from util.queryParse import parseQuery
from configuration.models import Configuration

from io import BytesIO
from PIL import Image
from subprocess import Popen, PIPE
from io import StringIO
import base64

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
    year = ""
    award = ""
    grade = 0

    if "grade" in request.GET and request.GET["grade"]:
        if "year" in request.GET and request.GET["year"]:
            query += "grade_" + request.GET["grade"] + "_year:" + request.GET["year"] + " "
            year = request.GET["year"]
            grade = request.GET["grade"]
        else:
            query += "grade:" + request.GET["grade"] + " "
    if "cumulative" in request.GET and request.GET["cumulative"]:
        if "year" in request.GET and request.GET["year"]:
            query += "award_" + request.GET["grade"] + ":" + request.GET["cumulative"] + " "
            award = request.GET["cumulative"]
        else:
            query += "award" + ":" + request.GET["cumulative"] + " "
    if "annual" in request.GET and request.GET["annual"]:
        query += "annual_cert:" + request.GET["annual"] + "_" + request.GET["grade"] + " "
        award = request.GET["annual"]

    students = parseQuery(query)

    awards_dict = {
        ":": " ",
        "_": " ",
        "annual cert": "annual",
        "grade": "gr",
        "award": "",
        "year": "",
        "SE": "Service",
        "AT": "Athletics",
        "SC": "Scholarship",
        "FA": "Fine Arts",

    }
    award_formatted = award
    for key, value in awards_dict.items():
        query = query.replace(key, value)
    for key, value in awards_dict.items():
        award_formatted = award_formatted.replace(key, value)

    config = Configuration.objects.get()

    with open(config.principal_signature.path, 'rb') as img:
        p_sig_string = str(base64.b64encode(img.read()))[2:-1]

    context = {
        'student_list': students,
        'type': query.title(),
        'year': year,
        'award': award,
        "grade": int(grade),
        'award_formatted': award_formatted,
        "principals_signature": p_sig_string,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def print_grad(request):
    template = get_template('export/print-grad.html')

    year = request.GET.get("year")
    grade = request.GET.get("grade")
    award = request.GET.get("grad-awards")

    query = f"grade_12_year:{year}"
    students = parseQuery(query)

    students = sorted(students, key=lambda student: student.SE_11_12_total, reverse=True)[:30]

    context = {
        'student_list': students,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def print_trophies(request):
    template = get_template('export/print-trophies.html')

    query = ""
    students = parseQuery(query)

    context = {
        'student_list': students[:2],
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
    award_type_display = award_type or ""
    year = ""

    if "year" in request.GET and request.GET["year"]:
        year = request.GET["year"]
        query += "grade_" + str(grade).zfill(2) + "_year:" + request.GET["year"] + " "
    else:
        query += "grade:" + str(grade) + " "

    students = parseQuery(query)

    # print(students[:10])

    # filter out students with no points of the right type
    new_students = students
    for s in students:
        if len(s.grade_set.get(grade=grade).points_set.filter(type__catagory=award_type)) == 0:
            new_students = new_students.exclude(id=s.id)
    students = new_students

    awards_dict = {
        "AT": "Athletics",
        "SE": "Service",
        "FA": "Fine Arts",
        "SC": "Scholarship",
    }
    for key, value in awards_dict.items():
        award_type_display = award_type_display.replace(key, value)

    context = {
        'student_list': students,
        'grade_num': grade,
        'award_type': award_type,
        'award_type_display': award_type_display,
        'year': year,
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
