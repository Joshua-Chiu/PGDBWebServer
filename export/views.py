from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse

from data.models import Student, PointCodes
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
        # print(request.GET)
        if "year" in request.GET and request.GET["year"]:
            award = request.GET["athletic"]
            if "cumulative" in request.GET["athletic"]:
                pass
            elif "ST" in request.GET["athletic"]:
                query += f"annual_cert:{request.GET['athletic']}_{request.GET['grade']}"
            else:
                query += "award_" + request.GET["grade"] + ":" + request.GET["athletic"] + " "
        else:
            query += "award" + ":" + request.GET["athletic"] + " "

    print(award)
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
        "bigblock": "big block",
        "cumulative": "Cumulative",
        "3ST": "3-Sport",
        "3+ST": "3+-Sport",
        "4ST": "4-Sport",
        "4+ST": "4+-Sport",
    }
    award_formatted = award
    if query:
        for key, value in awards_dict.items():
            award_formatted = award_formatted.replace(key, value)

        query = f"GRADE{grade} {year}-{int(year) + 1} "

        if any(award in s for s in ["SE", "AT", "FA", ]):
            print(award)
            query += f"{award_formatted.upper()} CERTIFICATE RECIPIENTS"
        elif any(award in s for s in ["honourroll"]):
            query += f"HONOUR ROLL CERTIFICATE RECIPIENTS"
        elif any(award in s for s in ["principalslist"]):
            query += f"PRINCIPALS LIST CERTIFICATE RECIPIENTS"
        elif any(award in s for s in ["silver", "gold", "platinum"]):
            query += f"{award_formatted.upper()} PIN RECIPIENTS"
        elif any(award in s for s in ["goldplus"]):
            query += f"{'GOLD PLUS'} BAR RECIPIENTS"
        else:
            query += f"{award_formatted.upper()} RECIPIENTS"
    config = Configuration.objects.get()

    with open(config.principal_signature.path, 'rb') as img:
        p_sig_string = str(base64.b64encode(img.read()))[2:-1]

    context = {
        'student_list': students,
        'type': query,  # title
        'year': year,
        'award': award,
        "grade": int(grade),
        'award_formatted': award_formatted,  # Certificate
        "principals_signature": p_sig_string,
    }
    return HttpResponse(template.render(context, request))


def print_grad(request):
    template = get_template('export/print-grad.html')
    students, query = "", ""
    year = request.GET.get("year")
    award = request.GET.get("grad-awards")

    if request.GET:
        query = f"grade_12_year:{year} active:both"
        students = parseQuery(query)

        if award != "ME" and award != "SUPER":
            students = sorted(students, key=lambda student: getattr(student, f"{award}_11_12_total"), reverse=True)[:30]
        elif award == "ME":
            students = sorted(students, key=lambda student: getattr(student, "all_11_12_total"), reverse=True)[:30]

        awards_dict = {
            "SE": "SERVICE",
            "AT": "ATHLETICS",
            "SC": "SCHOLARSHIP",
            "FA": "FINE ARTS",
            "ME": "MERIT",
            "SUPER": "SR. AWARDS SUPERLIST"
        }

        query = f"{year} - {int(year) + 1} {awards_dict[award]} GRADUATION CANDIDATES"

    context = {
        'student_list': students,
        'point_type': award,
        'year': year,
        'award': award,
        'type': query,
    }
    return HttpResponse(template.render(context, request))


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
    return HttpResponse(template.render(context, request))


def print_term(request):
    template = get_template('export/print-term.html')
    students, query, grade, year, term, roll = "", "", "", "", "", ""
    if request.GET:
        year = request.GET.get("year")
        grade = int(request.GET.get("grade"))
        term = int(request.GET.get("term"))
        roll = request.GET.get("roll")

        query = f"grade_{str(grade).zfill(2)}_year:{year} grade{str(grade).zfill(2)}_term{term}:{roll} active:both"
        students = parseQuery(query)

    context = {
        'grade': grade,
        'year': year,
        'term': term,
        'roll': roll,
        'student_list': students,
    }
    return HttpResponse(template.render(context, request))


def print_cslist(request):
    template = get_template('export/print-cslist.html')
    students, grade, year, se_point_code, at_point_code, fa_point_code = "", "", "", "", "", ""
    if request.GET:
        year = request.GET.get("year")
        grade = (request.GET.get("grade")).zfill(2)
        se_point_code = int(request.GET.get("service")) if request.GET.get("service") else None
        at_point_code = int(request.GET.get("athletic")) if request.GET.get("athletic") else None
        fa_point_code = int(request.GET.get("fine_arts")) if request.GET.get("fine_arts") else None

        query = f"grade_{grade}_year:{year} active:both "
        if se_point_code: query += f"grade_{grade}_point:SE_{se_point_code} "
        if at_point_code: query += f"grade_{grade}_point:AT_{at_point_code} "
        if fa_point_code: query += f"grade_{grade}_point:FA_{fa_point_code} "

        students = parseQuery(query)

    context = {
        'student_list': students,
        'points_se': PointCodes.objects.filter(catagory="SE"),
        'points_at': PointCodes.objects.filter(catagory="AT"),
        'points_fa': PointCodes.objects.filter(catagory="FA"),
        'grade': grade,
        'year': year,
        'se_point_code': se_point_code,
        'at_point_code': at_point_code,
        'fa_point_code': fa_point_code,
    }
    return HttpResponse(template.render(context, request))


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
    return HttpResponse(template.render(context, request))


def export_files(request):
    template = get_template('export/files.html')
    context = {

    }
    return HttpResponse(template.render(context, request))
