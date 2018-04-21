from django.shortcuts import render
from django.http import HttpResponse
from .models import Student
from django.template.loader import get_template

'''
def index(request):
    students = Student.objects.all()
    html = "<h1>Students</h1>"
    for s in students:
        html += "<p>{1} {2} #{0}</p>".format(s.student_num, s.first, s.last)
    return HttpResponse(html)
'''


def search(request, num):
    template = get_template('test2/student_list.html')
    context = {'student_list': Student.objects.filter(student_num=num)}
    return HttpResponse(template.render(context, request))


def student_info(request, num):
    template = get_template('test2/student_list.html')
    context = {'student_list': Student.objects.filter(id=num)}
    return HttpResponse(template.render(context, request))


def index(request):
    template = get_template('test2/student_list.html')
    context = {
        'student_list': Student.objects.all()
    }
    return HttpResponse(template.render(context, request))


