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
    html = ""
    for s in filter(lambda x: x.student_num == num, Student.objects.all()):
        html += "<p>{0}</p>".format(s.first)
    return HttpResponse(html)


def index(request):
    template = get_template('test2/index.html')
    context = {
        'Student': str(Student)
    }

    return HttpResponse(template.render(context, request))


