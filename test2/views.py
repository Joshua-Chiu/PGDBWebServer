from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
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


def search(request):
    template = get_template('test2/search.html')
    student_list = Student.objects.filter(first__icontains=request.GET['first'])
    context = {
        'student_list': student_list
    }
    return HttpResponse(template.render(context, request))


def student_info(request, num):
    template = get_template('test2/student_info.html')
    context = {
        'student': Student.objects.get(id=num)
    }
    return HttpResponse(template.render(context, request))


def student_submit(request, num):
    if request.method == 'POST':
        print("received POST request")
        for k, v in request.POST.items():
            print(k, "|", v)
    else:
        print("this is not supposed to happen don't do that again")

    template = get_template('test2/student_info.html')
    context = {
        'student': Student.objects.get(id=num)
    }
    return HttpResponseRedirect("/test2/student/{}".format(num))


def settings(request):
    template = get_template('test2/settings.html')
    context = {

    }
    return HttpResponse(template.render(context, request))


def index(request):
    template = get_template('test2/student_list.html')
    context = {
        'student_list': Student.objects.all()
    }
    return HttpResponse(template.render(context, request))


