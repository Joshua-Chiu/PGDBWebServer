import binascii
import os
import random

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetConfirmView
from axes.attempts import reset_user_attempts


def index(request):
    return HttpResponseRedirect('/')


def login(request):  # TODO this view is not being used
    print('hello')
    if request.method == 'POST':
        username = request.POST['username']  # get username
        password = request.POST['txtPwd']  # and password
        user = authenticate(request=request, username=username, password=password)  # checking username and pwd
        if user is not None:
            if user.is_active:
                user.first_visit = True
                user.save()
                login(request, user)


class PasswordResetConfirmView(PasswordResetConfirmView):
    def reset_attempts(self, *args):
        uidb64 = super().kwargs['uidb64']
        user = super().get_user(uidb64)
        reset_user_attempts(user)
        print(f"resetting now user {user}...")
        return self.reset_attempts()


def daniel_lai(request):
    if request.user.username == "dlai":
        request.user.first_name = "".join(random.choice([k.upper(), k.lower()]) for k in request.user.first_name)
        request.user.last_name = "".join(random.choice([k.upper(), k.lower()]) for k in request.user.last_name)
        # request.user.header_colour = f"#{'%06x' % random.randrange(16**6)}"
        # request.user.page_colour = f"#{'%06x' % random.randrange(16**6)}"
        # request.user.alternate_row_colour = f"#{'%06x' % random.randrange(16**6)}"
        # request.user.text_colour = f"#{'%06x' % random.randrange(16**6)}"
        # request.user.collapsible_bar_colour = f"#{'%06x' % random.randrange(16**6)}"
        request.user.save()
