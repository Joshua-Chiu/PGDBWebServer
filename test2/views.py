from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Student, PointCodes
from django.template.loader import get_template
from itertools import zip_longest

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
    if request.GET['query']:
        query = request.GET['query'].split(' ')
    else:
        query = []
    items = {}
    for i in query:
        term = i.split(':')
        if len(term) != 2:
            continue
        items[term[0]] = term[1]
    print(items)

    students = Student.objects.all()
    for k, v in items.items():
        if hasattr(Student, k):
            val = "{0}__icontains".format(k)
            print(val, v)
            students = students.filter(**{val: v})
        else:
            if k == 'grade':
                if len(v) == 1:
                    v = '0' + v
                print('homeroom__contains', v)
                students = students.filter(**{'homeroom__contains': v})

    context = {
        'student_list': students,
        'query': request.GET['query']
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


def codes(request):
    template = get_template('test2/codes.html')
    context = {'codes': PointCodes.objects.all()}
    return HttpResponse(template.render(context, request))


def codes_submit(request):
    print(list(request.POST.items()))
    items = list(request.POST.items())[1:]
    args = [iter(items)] * 3
    code_info = zip_longest(*args)
    print(list(code_info))

    for code in code_info:
        print(code[0][1])
    return HttpResponseRedirect("/test2/settings/codes")


def index(request):
    template = get_template('test2/student_list.html')
    context = {
        'student_list': Student.objects.all()
    }
    return HttpResponse(template.render(context, request))


