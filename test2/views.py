from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Student
from django.template.loader import get_template
from .forms import Search

'''
def index(request):
    students = Student.objects.all()
    html = "<h1>Students</h1>"
    for s in students:
        html += "<p>{1} {2} #{0}</p>".format(s.student_num, s.first, s.last)
    return HttpResponse(html)
'''


def search(request):
    if request.method == "GET":
        form = Search()
    else:
        # POST request not sure how it works
        form = Search(request)

    return render(request, 'test2/search.html', {'form': form})


def student_info(request, num):
    template = get_template('test2/student_info.html')
    context = {'student ': Student.objects.filter(id=num)[0]}
    return HttpResponse(template.render(context, request))


def index(request):
    template = get_template('test2/student_list.html')
    context = {
        'student_list': Student.objects.all()
    }
    return HttpResponse(template.render(context, request))


