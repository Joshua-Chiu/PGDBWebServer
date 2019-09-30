from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Student, PointCodes, PlistCutoff, Grade, Points
from users.models import CustomUser
from django.template.loader import get_template
from itertools import zip_longest
import datetime
import io
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from util.queryParse import parseQuery
from django.contrib.auth.decorators import login_required
from util.converter import wdb_convert

import dateutil.parser
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


@login_required()
def search(request):
    template = get_template('data/search.html')

    # if no query exists make an empty list
    if request.GET['query']:
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
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def student_info(request, num):
    template = get_template('data/student_info.html')
    context = {
        'student': Student.objects.get(id=num),
        'plists': PlistCutoff.objects.all()
    }
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


@login_required
def student_submit(request, num):
    entered_by = request.user
    student = Student.objects.get(id=num)
    items = list(request.POST.items())[1:]
    anecdotes = [item for item in items if item[0].find("anecdote") != -1]
    points_list = [item for item in items if item[0].find("points") != -1 or item[0].find("code") != -1]
    scholar_fields = [item for item in items if item[0].find("SC") != -1]
    points_list = points_list + scholar_fields
    code_delete_buttons = [item for item in items if item[0].find("deletePoint") != -1]

    # anecdotes
    for n, anecdote in enumerate(anecdotes):
        # print(anecdote[1])
        grade = student.grade_set.get(grade=int(student.homeroom[:2]) - n)
        grade.anecdote = anecdote[1]
        if request.user.has_perm('data.change_points'):
            grade.save()

    # delete codes buttons
    for button in code_delete_buttons:
        # buttons are ['deletepoint <grade> <catagory> <code> ', 'X']
        grade, catagory, code = button[0].strip().split(' ')[1:]
        point = \
            student.grade_set.get(grade=int(grade)).points_set.filter(type__catagory=catagory).filter(type__code=code)[
                0]
        if request.user.has_perm('data.change_points') or point.entered_by == request.user:
            point.delete()
        # print(point)
        # print("button: ", grade, type, code)

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
                grade = student.grade_set.get(grade=grade_num)
                scholar = grade.scholar_set.all()[0]
                scholar.term1 = t1
                scholar.term2 = t2
                if request.user.has_perm('data.change_scholar'):
                    scholar.save()
            else:
                if point_field[1] == '' or code_field[1] == '':
                    continue

                amount = float(point_field[1])
                code = int(code_field[1])

                # find the point class with the same code and category
                try:
                    typeClass = PointCodes.objects.filter(catagory=type).get(code=code)
                except PointCodes.DoesNotExist as e:
                    typeClass = PointCodes(catagory=type, code=code, description=str(type) + str(code))
                    if request.user.has_perm('data.add_PointCodes'):
                        typeClass.save()

                grade = student.grade_set.get(grade=grade_num)
                grade.points_set.create(type=typeClass, amount=amount, entered_by=entered_by)

    return HttpResponseRedirect(f"/data/student/{num}")


def archive(request):
    template = get_template('data/archive.html')
    context = {}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def archive_submit(request):
    logs = []
    if request.method == "POST":
        if request.user.has_perm('data.add_student'):
            if "file" in request.FILES:
                tree = ET.parse(request.FILES["file"])
                root = tree.getroot()

                # all students
                for s in root[0]:
                    try:
                        if len(Student.objects.filter(student_num=int(s[0].text))) != 0:
                            print(f"student with number {s[0].text} already exists")
                            logs.append(f"student with number {s[0].text} \t ({s[4].text}, {s[3].text}) already exists")
                            continue

                        s_obj = Student(
                            student_num=int(s[0].text),
                            homeroom=f"{s[1].text.zfill(2)}{s[2].text}",
                            first=s[3].text,
                            last=s[4].text,
                            legal=s[5].text,
                            sex=s[6].text,
                            grad_year=int(s[7].text)
                        )
                        s_obj.save()

                        for g in s[8]:
                            g_obj = Grade(
                                grade=int(g[0].text),
                                start_year=int(g[1].text),
                                anecdote=g[2].text or "",
                            )
                            s_obj.grade_set.add(g_obj, bulk=False)
                            g_obj.save()

                            g_obj.scholar_set.create(term1=float(g[3].text), term2=float(g[4].text))

                            for p in g[5]:  # fix so that the codes are the last 2 digits instead of last 4
                                if (len(PointCodes.objects.filter(catagory=p[0].text).filter(
                                        code=int(p[1].text))) == 0):
                                    type = PointCodes(catagory=p[0].text, code=int(p[1].text),
                                                      description=str(p[0].text) + str(p[1].text))
                                    type.save()
                                else:
                                    type = PointCodes.objects.filter(catagory=p[0].text).get(code=int(p[1].text))

                                g_obj.points_set.create(
                                    type=type,
                                    amount=float(p[2].text),
                                )
                        # print(f"added student {int(s[0].text)}")
                    except Exception as e:
                        student_num = int(s[0].text)
                        print(f"Failed to add student {int(s[0].text)}")
                        logs.append(f"Failed to add student {int(s[0].text)}")

                        # delete the partially formed student
                        if len(Student.objects.filter(student_num=student_num)) != 0:
                            Student.objects.get(student_num=student_num).delete()

                for plist in root[1]:
                    print(plist)
        else:
            logs.append("Permission error: Please make sure you can import students")

    template = get_template('data/archive.html')
    if not logs:
        logs.append("Import Successful")
    context = {
        "logs": logs,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def archive_wdb_submit(request):
    if request.method == "POST":
        if "file" in request.FILES:
            grade = int(request.POST["grade"])
            start_year = int(request.POST["start-year"])
            pgdb_file = wdb_convert((l.decode() for l in request.FILES["file"]), grade, start_year)

            response = HttpResponse(pgdb_file, content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=students.pgdb'

            return response

    return HttpResponseRedirect("/data/archive")


def archive_file(request):
    if not "query" in request.POST:
        raise Http404
    query = request.POST['query']

    print(f"query={query}")

    student_list = parseQuery(query)

    # plists from years that students being exported are in
    relevent_plists = []

    root = ET.Element('PGDB')

    students = ET.SubElement(root, "students")
    for student in student_list:
        student_tag = ET.SubElement(students, 'student')
        ET.SubElement(student_tag, 'number').text = str(student.student_num)
        ET.SubElement(student_tag, 'current_grade').text = str(student.homeroom[:-1])
        ET.SubElement(student_tag, 'homeroom').text = str(student.homeroom[-1:])
        ET.SubElement(student_tag, 'first').text = student.first
        ET.SubElement(student_tag, 'last').text = student.last
        ET.SubElement(student_tag, 'legal_name').text = student.legal
        ET.SubElement(student_tag, 'sex').text = student.sex
        ET.SubElement(student_tag, 'grad_year').text = str(student.grad_year)

        grades = ET.SubElement(student_tag, 'grades')
        for grade in student.grade_set.all():
            grade_tag = ET.SubElement(grades, 'grade')

            ET.SubElement(grade_tag, 'grade_num').text = str(grade.grade)
            ET.SubElement(grade_tag, 'start_year').text = str(grade.start_year)
            ET.SubElement(grade_tag, 'anecdote').text = str(grade.anecdote)

            ET.SubElement(grade_tag, 'AverageT1').text = str(grade.scholar_set.all()[0].term2)
            ET.SubElement(grade_tag, 'AverageT2').text = str(grade.scholar_set.all()[0].term1)

            points_tag = ET.SubElement(grade_tag, 'points')
            for point in grade.points_set.all():
                point_tag = ET.SubElement(points_tag, 'point')

                ET.SubElement(point_tag, 'catagory').text = str(point.type.catagory)
                ET.SubElement(point_tag, 'code').text = str(point.type.code)
                ET.SubElement(point_tag, 'amount').text = str(point.amount)

            # if a plist for this year exists add it to the list
            if grade.start_year not in relevent_plists and \
                    len(PlistCutoff.objects.filter(year=grade.start_year)) == 1:
                relevent_plists.append(grade.start_year)

    plists = ET.SubElement(root, "plists")
    for plist in relevent_plists:
        plist_object = PlistCutoff.objects.get(year=plist)
        plist_tag = ET.SubElement(plists, 'plist')

        ET.SubElement(plist_tag, 'year').text = str(plist)

        ET.SubElement(plist_tag, 'grade_8_T1').text = str(plist_object.grade_8_T1)
        ET.SubElement(plist_tag, 'grade_8_T2').text = str(plist_object.grade_8_T2)
        ET.SubElement(plist_tag, 'grade_9_T1').text = str(plist_object.grade_9_T1)
        ET.SubElement(plist_tag, 'grade_9_T2').text = str(plist_object.grade_9_T2)
        ET.SubElement(plist_tag, 'grade_10_T1').text = str(plist_object.grade_10_T1)
        ET.SubElement(plist_tag, 'grade_10_T2').text = str(plist_object.grade_10_T2)
        ET.SubElement(plist_tag, 'grade_11_T1').text = str(plist_object.grade_11_T1)
        ET.SubElement(plist_tag, 'grade_11_T2').text = str(plist_object.grade_11_T2)
        ET.SubElement(plist_tag, 'grade_12_T1').text = str(plist_object.grade_12_T1)
        ET.SubElement(plist_tag, 'grade_12_T2').text = str(plist_object.grade_12_T2)

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    xml_file = io.StringIO(xml_str)

    response = HttpResponse(xml_file, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=students.pgdb'

    return response


def settings(request):
    template = get_template('data/settings.html')
    context = {
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def codes(request):
    template = get_template('data/codes.html')
    context = {
        'codes': PointCodes.objects.all()
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def plist(request):
    template = get_template('data/plist.html')
    context = {
        'plist': PlistCutoff.objects.all(),
        'year': datetime.datetime.now().year,
        'month': datetime.datetime.now().month
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


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

        year.save()

    return HttpResponseRedirect("/data/settings/plist")


def autofocus_submit(request, num):
    user = CustomUser.objects.get(username=request.user.username)
    user.autofocus = num
    user.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


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

    return HttpResponseRedirect("/data/settings/codes")


def index(request):
    maintenance, notice = google_calendar()
    template = get_template('data/index.html')
    context = {
        'maintenance': maintenance,
        'notice': notice,
        'student_list': Student.objects.all(),
        'recent': Points.objects.all().order_by('-id')[:100],
    }

    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    elif request.user.is_authenticated:
        return HttpResponseRedirect('/entry')
    else:
        return HttpResponseRedirect('/')


def help(request):
    template = get_template('data/help.html')
    context = {}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def google_calendar():
    maintenance = []
    notice = []
    time_format = '%d %B, %H:%M %p'

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    SCOPES = 'https://www.googleapis.com/auth/calendar'

    secret = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/client_secret.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(filename=secret, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    service = build('calendar', 'v3', http=http)
    events = service.events().list(calendarId='pointgreydb@gmail.com', maxResults=10, timeMin=now, ).execute()
    events = events.get('items', [])

    for event in events:
        if "MAINTENANCE:" in event.get("summary"):
            maintenance.append({
                'action': event['summary'].replace("MAINTENANCE: ", ""),
                'note': event['description'],
                'start': dateutil.parser.parse(event["start"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
                'end': dateutil.parser.parse(event["end"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
            })
        else:
            notice.append({
                'title': event['summary'].replace("NOTICE: ", ""),
                'note': event['description'],
                'start': dateutil.parser.parse(event["start"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
                'end': dateutil.parser.parse(event["end"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
            })

    return maintenance, notice
