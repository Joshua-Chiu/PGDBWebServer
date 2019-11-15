from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login


def index(request):
    return HttpResponseRedirect('/')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']  # get username
        password = request.POST['txtPwd']  # and password
        user = authenticate(request=request, username=username, password=password)  # checking username and pwd
        if user is not None:
            if user.is_active:
                login(request, user)

