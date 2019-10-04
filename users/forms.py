from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('username', 'email',)


class CustomUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['email'].help_text = "Only enter an email if you grant user permission to self reset password."
        self.fields['password'].help_text = "Raw passwords are not stored, so there is no way to see this user's " \
                                            "password, but you can change the password using" \
                                            " <a href=\"../password/\">this form.</a>"

    class Meta:
        model = CustomUser
        fields = ('username', 'email',)
