from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse

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
        return HttpResponseRedirect(reverse('entry:error'))


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
    if "athletic" in request.GET and request.GET["athletic"]:
        print(request.GET)
        if "year" in request.GET and request.GET["year"]:
            if "ST" in request.GET["athletic"]:
                query += f"annual_cert:{request.GET['athletic']}_{request.GET['grade']}"
            else:
                query += "award_" + request.GET["grade"] + ":" + request.GET["athletic"] + " "
                award = request.GET["athletic"]
        else:
            query += "award" + ":" + request.GET["athletic"] + " "

    if query:
        students = parseQuery(query + " active:both")
    else:
        students = parseQuery(query)

    awards_dict = {
        "SE": "Service",
        "AT": "Athletics",
        "honourroll": "Scholarship",
        "principalslist": "Scholarship",
        "FA": "Fine Arts",
        "silver": "Silver Greyhound",
        "gold": "Gold Greyhound",
        "goldplus": "Gold Plus",
        "platinum": "Platinum",

    }
    award_formatted = award
    if query:
        for key, value in awards_dict.items():
            award_formatted = award_formatted.replace(key, value)

        if any(award in s for s in ["SE", "AT", "FA", ]):
            query = f"GRADE{grade} {year}-{int(year) + 1} {award_formatted.upper()} CERTIFICATE RECIPIENTS"
        elif any(award in s for s in ["honourroll", "principalslist", ]):
            query = f"GRADE{grade} {year}-{int(year) + 1} {award.upper()} CERTIFICATE RECIPIENTS"
        else:
            query = f"GRADE{grade} {year}-{int(year) + 1} {award_formatted.upper()} PIN RECIPIENTS"
    config = Configuration.objects.get()


    with open(config.principal_signature.path, 'rb') as img:
        p_sig_string = str(base64.b64encode(img.read()))[2:-1]

    context = {
        'student_list': students,
        'type': query,
        'year': year,
        'award': award,
        "grade": int(grade),
        'award_formatted': award_formatted,
        "principals_signature": p_sig_string,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def print_grad(request):
    template = get_template('export/print-grad.html')
    students, query = "", ""
    year = request.GET.get("year")
    award = request.GET.get("grad-awards")

    if request.GET:
        query = f"grade_12_year:{year} active:both"
        students = parseQuery(query)

        if not award == "ME":
            students = sorted(students, key=lambda student: getattr(student, f"{award}_11_12_total"), reverse=True)[:30]
        else:
            students = sorted(students, key=lambda student: getattr(student, "all_11_12_total"), reverse=True)[:30]

        awards_dict = {
            "SE": "SERVICE",
            "AT": "ATHLETICS",
            "SC": "SCHOLARSHIP",
            "FA": "FINE ARTS",
            "ME": "MERIT",
        }

        query = f"{year} - {int(year) + 1} {awards_dict[award]} GRADUATION CANDIDATES"

    context = {
        'student_list': students,
        'point_type': award,
        'year': year,
        'award': award,
        'type': query,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def print_trophies(request):
    template = get_template('export/print-trophies.html')

    year = request.GET.get("year")
    grade = request.GET.get("grade")
    award = request.GET.get("trophy-awards")

    if "grade" in request.GET and "year" in request.GET:
        query = f"grade_{grade.zfill(2)}_year:{year} active:both"
        students = parseQuery(query)

        students = sorted(students, key=lambda student: getattr(student.get_grade(grade), f"{award}_total"), reverse=True)[:30]
    else:
        students = Student.objects.none()

    context = {
        'student_list': students,
        'point_type': award,
        'year': year,
        'award': award,
        "grade": int(grade or 0),
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def print_term(request):
    template = get_template('export/print-term.html')
    students, query, grade, year, term, roll = "", "", "", "", "", ""
    if request.GET:
        year = request.GET.get("year")
        grade = int(request.GET.get("grade"))
        term = int(request.GET.get("term"))
        roll = request.GET.get("roll")

        query = f"grade_{str(grade).zfill(2)}_year:{year} grade{grade}_term{term}:{roll} active:both"
        students = parseQuery(query)

    context = {
        'grade': grade,
        'year': year,
        'term': term,
        'roll': roll,
        'student_list': students,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


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

    if query:
        students = parseQuery(query + " active:both")
    else:
        students = parseQuery(query)

    # print(students[:10])

    # filter out students with no points of the right type
    new_students = students
    if award_type != "SC":
        for s in students:
            if len(s.get_grade(grade).points_set.filter(type__catagory=award_type)) == 0:
                new_students = new_students.exclude(id=s.id)
        students = new_students
    else:
        for s in students:
            if s.get_grade(grade).term1_avg == 0 and s.get_grade(grade).term2_avg == 0:
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
        return HttpResponseRedirect(reverse('entry:error'))


def export_files(request):
    template = get_template('export/files.html')
    context = {

    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')
