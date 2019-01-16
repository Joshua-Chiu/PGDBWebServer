from django.http import HttpResponse, HttpResponseRedirect


def test2(request):
    return HttpResponseRedirect('/test2/')


def accounts(request):
    return HttpResponseRedirect('/accounts/login')



