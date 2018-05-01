from django import forms
from .models import Post

class ServiceForm(forms.Form):
    service = forms.CharField(label='Service', max_length=100)