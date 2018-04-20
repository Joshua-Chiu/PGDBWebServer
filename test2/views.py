from django.shortcuts import render
from django.http import HttpResponse
from .models import Student


def index(request):
    students = Student.objects.all()
    html = "<h1>students</h1>"
    for s in students:
        html += "<p>{0}</p>".format(s.student_num)
    return HttpResponse(html)

