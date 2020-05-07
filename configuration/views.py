from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import os, pytz, datetime
from django.template.loader import render_to_string, get_template
from django.urls import reverse
import dateutil.parser
import httplib2, threading
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from PGDBWebServer.settings import BUILD_NUMBER
from data.models import *
offline_status = False

integrity_data = []


def help(request):
    template = get_template('configuration/help.html')
    context = {
        'build': BUILD_NUMBER,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def google_calendar():
    maintenance = []
    notice = []

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    SCOPES = 'https://www.googleapis.com/auth/calendar'

    global offline_status
    offline_status = False
    secret = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          '../PGDBWebServer/ServerConfig/client_secret.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(filename=secret, scopes=SCOPES)
    http = credentials.authorize(httplib2.Http())
    service_now = [pytz.utc.localize(datetime.datetime(1970, 1, 1)).astimezone(pytz.timezone('America/Vancouver')),
                   pytz.utc.localize(datetime.datetime(1970, 1, 1)).astimezone(pytz.timezone('America/Vancouver'))]
    try:
        service = build('calendar', 'v3', http=http)
        events = service.events().list(calendarId='pointgreydb@gmail.com', maxResults=10, timeMin=now, singleEvents=True,
                                       orderBy='startTime').execute()
        events = events.get('items', [])
        now = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone('America/Vancouver'))

        for event in events:
            if "MAINTENANCE:" in event.get("summary"):
                maintenance.append({
                    'action': event['summary'].replace("MAINTENANCE: ", "") if 'summary' in event else "",
                    'note': event['description'] if 'description' in event else "",
                    'start': dateutil.parser.parse(event["start"]["dateTime"]).strftime("%d %b, %Y %H:%M"),
                    'end': dateutil.parser.parse(event["end"]["dateTime"]).strftime("%d %b, %Y %H:%M"),
                })
                service_now[0] = dateutil.parser.parse(event["start"]["dateTime"])
                service_now[1] = dateutil.parser.parse(event["end"]["dateTime"])
                if service_now[0] < now < service_now[1]:
                    offline_status = True
            else:
                notice.append({
                    'title': event['summary'].replace("NOTICE: ", "") if 'summary' in event else "",
                    'note':  event['description'] if 'description' in event else "",
                    'start': dateutil.parser.parse(event["start"]["dateTime"]).strftime("%d %b, %Y %H:%M"),
                    'end': dateutil.parser.parse(event["end"]["dateTime"]).strftime("%d %b, %Y %H:%M"),
                })
                # except httplib2.ServerNotFoundError or httplib2.HttpLib2Error:
    except Exception as e:
        print(e)
        notice = [{'title': "ERR", 'note': "Please check your internet connection", 'start': "--:--", 'end': "-", }]

    # Current date in UTC
    #print(offline_status)

    return maintenance, notice, offline_status


def offline(request):
    maintenance, notice, status = google_calendar()
    if status:
        request.user.first_visit = False
        request.user.save()
        context = {
            'maintenance': maintenance[0],
        }
        return HttpResponse(get_template('configuration/offline.html').render(context, request))
    return HttpResponseRedirect(reverse('data:index'))


def intergrity_check(request):
    check = threading.Thread(target=check_integrity, args=())
    check.start()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def check_integrity():
    global integrity_data
    integrity_data = []
    integrity_data.append(f"Last ran: {datetime.datetime.now()}")
    for student in Student.objects.all():
        for grade in student.all_grades:
            temp = grade.SE_total
            grade.calc_points_total("SE")
            if not temp == grade.SE_total: integrity_data.append(f"{student}: Fixed service totalling points {grade.grade}.")

            temp = grade.AT_total
            grade.calc_points_total("AT")
            if not temp == grade.AT_total: integrity_data.append(f"{student}: Fixed athletic totalling points {grade.grade}.")

            temp = grade.FA_total
            grade.calc_points_total("FA")
            if not temp == grade.FA_total: integrity_data.append(f"{student}: Fixed fine arts points totalling {grade.grade}.")

            temp = grade.SC_total
            grade.calc_SC_total()
            if not temp == round(grade.SC_total, 3): integrity_data.append(f"{student}: Fixed scholar points totalling {grade.grade}.")

            if not 0 <= grade.term1_avg < 100: integrity_data.append(f"{student}: Grade {grade.grade} average Term 1 invalid")
            if not 0 <= grade.term2_avg < 100: integrity_data.append(f"{student}: Grade {grade.grade} average Term 2 invalid")
        # integrity_data.append(f"{student}: Check OK")

    for plist in PlistCutoff.objects.all():
        if not 0 <= plist.grade_8_T1 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 8 T1 invalid")
        if not 0 <= plist.grade_9_T1 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 9 T1 invalid")
        if not 0 <= plist.grade_10_T1 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 10 T1 invalid")
        if not 0 <= plist.grade_11_T1 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 11 T1 invalid")
        if not 0 <= plist.grade_12_T1 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 12 T1 invalid")
        if not 0 <= plist.grade_8_T2 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 8 T2 invalid")
        if not 0 <= plist.grade_9_T2 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 9 T2 invalid")
        if not 0 <= plist.grade_10_T2 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 10 T2 invalid")
        if not 0 <= plist.grade_11_T2 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 11 T2 invalid")
        if not 0 <= plist.grade_12_T2 <= 100: integrity_data.append(f"Plist: Grade {plist.year} average Term 12 T2 invalid")
    integrity_data.append(f"Check completed: {datetime.datetime.now()}")


def integrity_report(request):
    global integrity_data
    template = get_template('configuration/integrity.html')
    context = {
        'integrity_data': integrity_data,
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect(reverse('entry:error'))


def handle_exception_40X(request, exception):
    context = {
        'exception': exception,
    }
    return HttpResponse(get_template('configuration/offline.html').render(context, request))


def handle_exception_50X(request):
    context = {

    }
    return HttpResponse(get_template('configuration/offline.html').render(context, request))


def csrf_failure(request, reason=""):
    return HttpResponseRedirect('/')
