from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from datetime import datetime
from configuration.views import google_calendar
from .models import Student, PointCodes, PlistCutoff, Grade, Points, LoggedAction
from configuration.models import Configuration
from itertools import zip_longest
import io
import xml.dom.minidom as minidom
from util.queryParse import parseQuery
from django.contrib.auth.decorators import login_required, user_passes_test
from util.converter import wdb_convert
from util.roll_converter import roll_convert
from threading import Thread

from .extra_views import *

export_file_thread = 0
logs = []


def search(request):
    template = get_template('data/search.html')

    # if no query exists make an empty list
    if "query" in request.GET and request.GET['query']:
        query = request.GET['query']
    else:
        return HttpResponse(template.render(None, request))

    students = parseQuery(query)

    if len(students) == 1:
        return HttpResponseRedirect(f"/data/student/{students[0].id}")
    context = {
        'student_list': students,
        'query': request.GET['query']
    }
    return HttpResponse(template.render(context, request))


def student_info(request, num):
    template = get_template('data/student_info.html')
    student = Student.objects.get(id=num)
    context = {
        'student': student,
        'plists': PlistCutoff.objects.all(),
        'config': Configuration.objects.get(),
        'grade_12': student.get_grade(12),
        'grade_11': student.get_grade(11),
        'grade_10': student.get_grade(10),
        'grade_09': student.get_grade(9),
        'grade_08': student.get_grade(8),

    }
    return HttpResponse(template.render(context, request))


def student_submit(request, num):
    if request.user.no_entry: return HttpResponseRedirect(f"/data/student/{num}")
    entered_by = request.user
    student = Student.objects.get(id=num)
    items = list(request.POST.items())
    anecdotes = [item for item in items if "anecdote" in item[0] != -1]
    points_list = [item for item in items if item[0].find("points") != -1 or item[0].find("code") != -1]
    scholar_fields = [item for item in items if item[0].find(" SC ") != -1]
    points_list = points_list + scholar_fields
    code_delete_buttons = [item for item in items if item[0].find("deletePoint") != -1]
    nullification = dict(item for item in items if item[0].find("nullify") != -1)

    # anecdotes
    for n, anecdote in enumerate(anecdotes):
        grade = student.get_grade(student.cur_grade_num - n)
        grade.anecdote = anecdote[1]
        grade.save()

    # delete codes buttons
    for button in code_delete_buttons:
        # buttons are ['deletepoint <grade> <catagory> <code> ', 'X']
        id = int(button[0].strip().split(' ')[1])
        point = Points.objects.get(id=id)
        point.delete(request.user)
        point.Grade.calc_points_total(point.type.catagory)

    # points and codes
    if request.method == 'POST':
        # print("received POST request")
        # for k, v in request.POST.items():
        #     print(k, "|", v)

        # iterate through pairs of point amount and code
        for point_field, code_field in zip(points_list[::2], points_list[1::2]):

            # get info like grade and point type e.g. SE, AT
            info = point_field[0].split(' ')
            grade_num = int(info[0])
            type = info[1]

            # decide if it's scholar or other type
            if type == "SC":
                # scholar gets its own class from the other points
                if point_field[1] == '' and code_field[1] == '':
                    continue

                if point_field[1] == '':
                    t1 = 0
                else:
                    t1 = float(point_field[1])

                if code_field[1] == '':
                    t2 = 0
                else:
                    t2 = float(code_field[1])

                # set the scholar average
                grade = student.get_grade(grade_num)
                grade.term1_avg = t1
                grade.term2_avg = t2
                if t1 <= 100 and t2 <= 100: grade.save()

            else:
                if point_field[1] == '' or code_field[1] == '':
                    continue

                amount = float(point_field[1])
                code = int(code_field[1])

                # skip over invalid entries
                success = True if type == "SE" or (type == "AT" and amount <= 6) or (type == "FA" and amount <= 10) else False
                if not success: continue

                # find the point class with the same code and category
                try:
                    typeClass = PointCodes.objects.filter(catagory=type).get(code=code)
                except PointCodes.DoesNotExist as e:
                    typeClass = PointCodes(catagory=type, code=code, description=str(type) + str(code))
                    typeClass.save()

                grade = student.get_grade(grade_num)
                grade.add_point(Points(type=typeClass, amount=amount, entered_by=entered_by), request.user)

    for grade_num in range(8, int(student.cur_grade_num) + 1):
        grade = student.get_grade(grade_num)
        grade.isnull_AT = f"AT{grade_num} nullify" not in nullification
        print(f"SC{grade_num} nullify" not in nullification)
        grade.isnull_FA = f"FA{grade_num} nullify" not in nullification
        grade.isnull_SC = f"SC{grade_num} nullify" not in nullification
        grade.isnull_SE = f"SE{grade_num} nullify" not in nullification
        grade.isnull_term1 = f"SC{grade_num}T1 nullify" not in nullification
        grade.isnull_term2 = f"SC{grade_num}T2 nullify" not in nullification

        grade.calc_points_total("SE")
        grade.calc_points_total("AT")
        grade.calc_points_total("FA")
        grade.calc_SC_total()

        grade.save()

    return HttpResponseRedirect(f"/data/student/{num}")


def archive(request):
    template = get_template('data/archive.html')
    context = {}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def archive_submit(request):
    global logs
    logs = []
    if request.method == "POST":
        if request.user.has_perm('data.add_student'):
            if "file" in request.FILES:
                file = ET.parse(request.FILES["file"])
                import_thread = Thread(target=import_pgdb_file, args=(file, request.user, ))
                import_thread.start()
                LoggedAction(user=request.user, message=f"File: PGDB Backup File uploaded by {request.user}").save()
                logs.append("We will now import the file in the background")
        else:
            logs.append("Permission error: Please make sure you can import students")
    template = get_template('data/file_upload.html')
    context = {
        "logs": logs,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def archive_wdb_submit(request):
    if request.method == "POST":
        if "file" in request.FILES:
            grade = int(request.POST["grade"])
            start_year = int(request.POST["start-year"])
            pgdb_file = wdb_convert((l.decode() for l in request.FILES["file"]), grade, start_year)

            response = HttpResponse(pgdb_file, content_type='application/xml')
            response['Content-Disposition'] = f'attachment; filename={request.FILES["file"].name.split(".", 1)[0]}.pgdb'

            return response

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def archive_file(request):
    global export_file_thread
    if "query" not in request.POST:
        raise Http404
    query = request.POST['query']

    print(f"query={query}")

    student_list = parseQuery(query)

    # plists from years that students being exported are in
    relevent_plists = []

    export_file_thread = export_pgdb_archive(student_list, relevent_plists)

    xml_str = minidom.parseString(ET.tostring(export_file_thread)).toprettyxml(indent="  ")
    xml_file = io.StringIO(xml_str)

    response = HttpResponse(xml_file, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename={query or str(datetime.now().strftime("%Y-%m-%d %Hh%Mm%Ss"))}.pgdb'

    return response


def roll_importer(request):
    if request.method == "POST":
        if "file" in request.FILES:

            excluded = [x.strip() for x in request.POST.get("excluded-courses", "YCPM, YBMO, YIPS, MCE8, MCE9, MCLC").split(',')]

            roll_conv_thread = Thread(target=convert_roll, args=(request.POST["start-year"], request.POST["term"], request.FILES["file"], excluded, request, ))
            roll_conv_thread.start()
    template = get_template('data/file_upload.html')
    context = {
        "logs": logs,
    }
    LoggedAction(user=request.user, message=f"File: Honour Roll File uploaded by {request.user}").save()
    return HttpResponse(template.render(context, request))


def settings(request):
    template = get_template('data/settings.html')
    context = {
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def codes(request):
    template = get_template('data/codes.html')
    context = {
        'codes': PointCodes.objects.all()
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def plist(request):
    template = get_template('data/plist.html')
    context = {
        'plist': PlistCutoff.objects.all(),
        'year': datetime.now().year,
        'month': datetime.now().month
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def plist_submit(request):
    plist = PlistCutoff.objects.all()
    items = request.POST

    for year in plist:
        year.grade_8_T1 = items[str(year.year) + " 8 1"]
        year.grade_8_T2 = items[str(year.year) + " 8 2"]

        year.grade_9_T1 = items[str(year.year) + " 9 1"]
        year.grade_9_T2 = items[str(year.year) + " 9 2"]

        year.grade_10_T1 = items[str(year.year) + " 10 1"]
        year.grade_10_T2 = items[str(year.year) + " 10 2"]

        year.grade_11_T1 = items[str(year.year) + " 11 1"]
        year.grade_11_T2 = items[str(year.year) + " 11 2"]

        year.grade_12_T1 = items[str(year.year) + " 12 1"]
        year.grade_12_T2 = items[str(year.year) + " 12 2"]

        year.save(request.user)

    return HttpResponseRedirect(reverse('data:plist'))


def codes_submit(request):
    # sort the codes into a list where each code is an item
    items = list(request.POST.items())[1:]
    args = [iter(items)] * 3
    code_info = list(zip_longest(*args))

    for code in code_info:
        if (not code[0][1]) or (not code[1][1]):
            continue

        # if there is an already existing code don't create a new one
        filter_codes = PointCodes.objects.filter(code=int(code[1][1]))
        filter_codes = filter_codes.filter(catagory=code[0][1])
        if len(filter_codes) == 1:
            entry = filter_codes[0]
        elif len(filter_codes) == 0:
            entry = PointCodes()
        else:
            print("panic!!")

        entry.code = code[1][1]
        entry.catagory = code[0][1].upper()
        entry.description = code[2][1]
        entry.save()

    return HttpResponseRedirect(reverse('data:codes'))


def index(request):
    maintenance, notice, offline = google_calendar()
    if offline and request.user.first_visit:
        return HttpResponseRedirect(reverse("configuration:offline"))
    if request.user.is_superuser:
        template = get_template('data/index.html')
        context = {
            'maintenance': maintenance,
            'notice': notice,
            'student_list': Student.objects.all(),
            'recent': Points.objects.all().order_by('-id')[:100],
            'logs': LoggedAction.objects.all().order_by('-id')[:100],
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:index'))
