from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import os, pytz, datetime
from django.template.loader import render_to_string, get_template
from django.urls import reverse
import dateutil.parser
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from PGDBWebServer.settings import BUILD_NUMBER
offline_status = False


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
    secret = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/client_secret.json')
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
                    'action': event['summary'].replace("MAINTENANCE: ", ""),
                    'note': event['description'],
                    'start': dateutil.parser.parse(event["start"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
                    'end': dateutil.parser.parse(event["end"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
                })
                service_now[0] = dateutil.parser.parse(event["start"]["dateTime"])
                service_now[1] = dateutil.parser.parse(event["end"]["dateTime"])
                if service_now[0] < now < service_now[1]:
                    offline_status = True
            else:
                notice.append({
                    'title': event['summary'].replace("NOTICE: ", ""),
                    'note': event['description'],
                    'start': dateutil.parser.parse(event["start"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
                    'end': dateutil.parser.parse(event["end"]["dateTime"]).strftime("%d %b, %Y %H:%M%p"),
                })
    # except httplib2.ServerNotFoundError or httplib2.HttpLib2Error:
    except Exception as e:
        notice = [{'title': "ERR", 'note': "Please check your internet connection", 'start': "--:--", 'end': "-", }]

    # Current date in UTC
    # print(offline_status)

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
