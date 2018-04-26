from django import forms


class ServiceForm(forms.Form):
    service = forms.CharField(label='Service', max_length=100)


class Search(forms.Form):
    first = forms.CharField(label='first', max_length=30)
