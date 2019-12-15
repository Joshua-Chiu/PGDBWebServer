from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import PasswordResetConfirmView
from axes.attempts import reset_user_attempts

def index(request):
    return HttpResponseRedirect('/')


def login(request):  # TODO this view is not being used
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

