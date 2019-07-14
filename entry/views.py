from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from data.models import Student, PointCodes
from django.http import JsonResponse


def checkUser(user, category):
    return user.groups.filter(name=category).exists() or user.is_superuser


def index(request):
    template = get_template('entry/index.html')
    context = {
    }
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def service(request):
    if request.user.is_authenticated and checkUser(request.user, "Service"):
        template = get_template('entry/service.html')
        context = {
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def athletics(request):
    if request.user.is_authenticated and checkUser(request.user, "Athletics"):
        template = get_template('entry/athletics.html')
        context = {
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def fine_arts(request):
    if request.user.is_authenticated and checkUser(request.user, "Fine Arts"):
        template = get_template('entry/fine-arts.html')
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def scholar(request):
    if request.user.is_authenticated and checkUser(request.user, "Scholar"):
        template = get_template('entry/scholar.html')
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def error(request):
    template = get_template('entry/error.html')
    context = {}
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/data')


def upload_file(request, point_catagory):
    if request.method == "POST":
        if "file" in request.FILES:
            for line in request.FILES['file']:
                #if it's the start line skip it
                if line.decode("utf-8") == "student_number	code	amount\n":
                    continue

                # print(line.decode("utf-8").strip())
                snum, code, amount = line.decode("utf-8").strip().split("\t")

                student = Student.objects.get(student_num=snum)
                grade = student.grade_set.get(grade=int(student.homeroom[:2]))

                # create point type if missing
                try:
                    point_type = PointCodes.objects.filter(catagory=point_catagory).get(code=code)
                except PointCodes.DoesNotExist:
                    point_type = PointCodes(catagory=point_catagory, code=code, description="")
                    point_type.save()

                grade.points_set.create(type=point_type, amount=amount)

    return HttpResponseRedirect('/entry/service')


def get_student_name(request):
    student_id = request.GET.get('student_id', None)
    print(student_id)
    data = {
        'exists': Student.objects.filter(student_num__iexact=student_id).exists(),
        'name': Student.objects.filter(student_num__iexact=student_id).first,
    }
    return JsonResponse(data)
