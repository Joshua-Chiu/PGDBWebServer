from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import os
import datetime
from .models import Student

import dateutil.parser
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


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


def ajax_import_status(request):
    data = {
        'status': "10%",
    }
    return JsonResponse(data)


def ajax_student_cumulative_data(request):
    snum = request.GET.get('student_num', None)
    student = Student.objects.get(student_num=snum)
    data = {
        'silver': student.silver_pin,
        'gold': student.gold_pin,
        'goldplus': student.goldPlus_pin,
        'platinum': student.platinum_pin,
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
        'gradAVG': float(round(student.average_11_12, 2)),
        'gradSE': round(student.SE_11_12_total, 2),
        'gradAT': round(student.AT_11_12_total, 2),
        'gradSC': round(student.SC_11_12_total, 2),
        'gradFA': round(student.FA_11_12_total, 2),
        'gradTOTAL': round(sum([student.SE_11_12_total, student.AT_11_12_total, student.SC_11_12_total, student.FA_11_12_total]), 2),
    }
    return JsonResponse(data)

