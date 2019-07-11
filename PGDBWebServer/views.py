from django.http import HttpResponse, HttpResponseRedirect


def data(request):
    return HttpResponseRedirect('/data/')


def accounts(request):
    return HttpResponseRedirect('/accounts/login')



