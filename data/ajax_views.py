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
    }
    return JsonResponse(data)

