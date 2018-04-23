from django import forms

class ServiceForm(forms.Form):
    service = forms.CharField(label='Service', max_length=100)