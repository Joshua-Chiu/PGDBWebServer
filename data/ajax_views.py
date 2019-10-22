from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import os
import datetime
from .models import Student, PointCodes, PlistCutoff

from django.db import close_old_connections
import xml.etree.ElementTree as ET
import dateutil.parser
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from axes.utils import reset

logs = []
done = False


def google_calendar():
    maintenance = []
    notice = []

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    SCOPES = 'https://www.googleapis.com/auth/calendar'

    secret = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/client_secret.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(filename=secret, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    try:
        service = build('calendar', 'v3', http=http)
        events = service.events().list(calendarId='pointgreydb@gmail.com', maxResults=10, timeMin=now, singleEvents=True,
                                       orderBy='startTime').execute()
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
    except httplib2.ServerNotFoundError:
        notice = [{'title': "ERR", 'note': "Please check your internet connection", 'start': "--:--", 'end': "-", }]

    return maintenance, notice


def ajax_student_points_data(request):
    #  snum = request.GET.get('student_num', None)
    #  student = Student.objects.get(student_num=snum)
    data = {}
    return JsonResponse(data)


def ajax_student_cumulative_data(request):
    snum = request.GET.get('student_num', None)
    student = Student.objects.get(student_num=snum)
    grade = int("".join(filter(str.isdigit, student.homeroom)))
    data = {
        'silver': student.silver_pin,
        'gold': student.gold_pin,
        'goldplus': None,
        'platinum': None,
        'bigblock': student.bigblock_award,
        'TOTAL08': round(sum([student.get_cumulative_SE(8), student.get_cumulative_AT(8),
                              student.get_cumulative_SC(8), student.get_cumulative_FA(8)]), 2),
        'TOTAL09': round(sum([student.get_cumulative_SE(9), student.get_cumulative_AT(9),
                              student.get_cumulative_SC(9), student.get_cumulative_FA(9)]), 2),
        'TOTAL10': round(sum([student.get_cumulative_SE(10), student.get_cumulative_AT(10),
                              student.get_cumulative_SC(10), student.get_cumulative_FA(10)]), 2),
        'TOTAL11': round(sum([student.get_cumulative_SE(11), student.get_cumulative_AT(11),
                              student.get_cumulative_SC(11), student.get_cumulative_FA(11)]), 2),
        'TOTAL12': round(sum([student.get_cumulative_SE(12), student.get_cumulative_AT(12),
                              student.get_cumulative_SC(12), student.get_cumulative_FA(12)]), 2),
        'SE08': round(student.get_cumulative_SE(8), 2),
        'SE09': round(student.get_cumulative_SE(9), 2),
        'SE10': round(student.get_cumulative_SE(10), 2),
        'SE11': round(student.get_cumulative_SE(11), 2),
        'SE12': round(student.get_cumulative_SE(12), 2),
        'AT08': round(student.get_cumulative_AT(8), 2),
        'AT09': round(student.get_cumulative_AT(9), 2),
        'AT10': round(student.get_cumulative_AT(10), 2),
        'AT11': round(student.get_cumulative_AT(11), 2),
        'AT12': round(student.get_cumulative_AT(12), 2),
        'SC08': round(student.get_cumulative_SC(8), 2),
        'SC09': round(student.get_cumulative_SC(9), 2),
        'SC10': round(student.get_cumulative_SC(10), 2),
        'SC11': round(student.get_cumulative_SC(11), 2),
        'SC12': round(student.get_cumulative_SC(12), 2),
        'FA08': round(student.get_cumulative_FA(8), 2),
        'FA09': round(student.get_cumulative_FA(9), 2),
        'FA10': round(student.get_cumulative_FA(10), 2),
        'FA11': round(student.get_cumulative_FA(11), 2),
        'FA12': round(student.get_cumulative_FA(12), 2),
    }
    if grade >= 12:
        grad = {
            'platinum': student.platinum_pin,
            'gradAVG': float(round(student.average_11_12, 2)),
            'gradSE': round(student.SE_11_12_total, 2),
            'gradAT': round(student.AT_11_12_total, 2),
            'gradSC': round(student.SC_11_12_total, 2),
            'gradFA': round(student.FA_11_12_total, 2),
            'gradTOTAL': round(
                sum([student.SE_11_12_total, student.AT_11_12_total, student.SC_11_12_total, student.FA_11_12_total]),
                2),
        }
        data.update(grad)
        data.update({'goldplus': student.goldPlus_pin, })
    elif grade >= 11:
        data.update({'goldplus': student.goldPlus_pin, })

    # add annual certificates to data dict
    for g in range(8, grade + 1):
        grade_object = student.grade_set.get(grade=g)
        data['annual SE ' + str(g).zfill(2)] = grade_object.SE_total
        data['annual AT ' + str(g).zfill(2)] = grade_object.AT_total
        data['annual FA ' + str(g).zfill(2)] = grade_object.FA_total
        data['annual SC ' + str(g).zfill(2)] = grade_object.SC_total

        data['annual HR ' + str(g).zfill(2)] = grade_object.scholar_set.get().term1 >= 79.45 and grade_object.scholar_set.get().term2 >= 79.45
        try:
            data['annual PL ' + str(g).zfill(2)] = grade_object.scholar_set.get().term1 >= grade_object.plist_T1 and \
                                              grade_object.scholar_set.get().term2 >= grade_object.plist_T2
        except PlistCutoff.DoesNotExist:
            data['annual PL ' + str(g).zfill(2)] = False

    return JsonResponse(data)


def export_pgdb_archive(student_list, relevent_plists):
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

    return root


def import_pgdb_file(tree):
    global logs
    global done
    done = False
    root = tree.getroot()
    # all students
    for s in root[0]:
        try:
            if len(Student.objects.filter(student_num=int(s[0].text))) != 0:
                print(f"Student with number {s[0].text} already exists")
                logs.append(f"Student with number {s[0].text} \t ({s[4].text}, {s[3].text}) already exists")
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

                g_obj = s_obj.grade_set.get(grade=int(g[0].text))
                g_obj.anecdote = g[2].text or ""

                scholar = g_obj.scholar_set.all().first()

                scholar.term1 = float(g[3].text)
                scholar.term2 = float(g[4].text)
                scholar.save()

                g_obj.save()

                for p in g[5]:  # fix so that the codes are the last 2 digits instead of last 4
                    if (len(PointCodes.objects.filter(catagory=p[0].text).filter(
                            code=int(p[1].text))) == 0):
                        type = PointCodes(catagory=p[0].text, code=int(p[1].text),
                                          description=str(p[0].text) + str(p[1].text))
                        type.save()
                    else:
                        type = PointCodes.objects.filter(catagory=p[0].text).get(code=int(p[1].text))

                    g_obj.points_set.create(type=type, amount=float(p[2].text), )
            logs.append(f"Added student {s[0].text} \t ({s[4].text}, {s[3].text}) successfully")
        except Exception as e:
            student_num = int(s[0].text)
            print(f"Failed to add student {int(s[0].text)}")
            logs.append(f"Failed to add student {s[0].text} \t ({s[4].text}, {s[3].text})")

            # delete the partially formed student
            if len(Student.objects.filter(student_num=student_num)) != 0:
                Student.objects.get(student_num=student_num).delete()

    for plist in root[1]:
        print(plist)

    done = True
    print(done)
    close_old_connections()


def ajax_import_status(request):
    if not done:
        data = {'done': 'false'}
        return JsonResponse(data)
    global logs
    data = {
        'logs': logs,
        'done': 'true'
    }

    return JsonResponse(data)


def reset_users(request):
    reset(request.GET['username'])
    return HttpResponseRedirect(request.path)
