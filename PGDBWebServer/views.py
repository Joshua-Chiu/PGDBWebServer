from django.http import HttpResponse, HttpResponseRedirect

def test2(request):
    return HttpResponseRedirect('/test2/')
