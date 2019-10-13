from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import os
import datetime
from .models import Student, PointCodes
import xml.etree.ElementTree as ET
import dateutil.parser
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

logs = []


def google_calendar():
    maintenance = []
    notice = []

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    SCOPES = 'https://www.googleapis.com/auth/calendar'

    secret = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/client_secret.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(filename=secret, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
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

    return maintenance, notice


def ajax_student_points_data(request):
    snum = request.GET.get('student_num', None)
    student = Student.objects.get(student_num=snum)
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
        'TOTAL08': round(sum([student.get_cumulative_SE(8), student.get_cumulative_AT(8), student.get_cumulative_SC(8), student.get_cumulative_FA(8)]), 2),
        'TOTAL09': round(sum([student.get_cumulative_SE(9), student.get_cumulative_AT(9), student.get_cumulative_SC(9), student.get_cumulative_FA(9)]), 2),
        'TOTAL10': round(sum([student.get_cumulative_SE(10), student.get_cumulative_AT(10), student.get_cumulative_SC(10), student.get_cumulative_FA(10)]), 2),
        'TOTAL11': round(sum([student.get_cumulative_SE(11), student.get_cumulative_AT(11), student.get_cumulative_SC(11), student.get_cumulative_FA(11)]), 2),
        'TOTAL12': round(sum([student.get_cumulative_SE(12), student.get_cumulative_AT(12), student.get_cumulative_SC(12), student.get_cumulative_FA(12)]), 2),
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

    return JsonResponse(data)


def import_pgdb_file(tree):
    global logs
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


def ajax_import_status(request):
    global logs
    data = {
        'logs': logs,
    }
    return JsonResponse(data)
