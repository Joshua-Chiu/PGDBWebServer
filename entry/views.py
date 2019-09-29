from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from data.models import Student, PointCodes, Points
from django.http import JsonResponse


def checkUser(user, category):
    return user.groups.filter(name=category).exists() or user.is_superuser


def index(request):
    template = get_template('entry/index.html')
    context = {
        'recent': Points.objects.filter(entered_by=request.user)
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
    logs = []
    entered_by = request.user
    if request.method == "POST":
        if "file" in request.FILES:
            for line in request.FILES['file']:
                # if it's the start line skip it
                if line.decode("utf-8") == "Student Number,Last Name,Minutes of Service,Code\n":
                    continue

                # print(line.decode("utf-8").strip())
                print(line.decode("utf-8").strip().split(","))
                snum, last_name, minutes, code = line.decode("utf-8").strip().split(",")[:4]

                points = minutes
                if point_catagory == "SE":  # divide by 300 only if it's SE
                    points = '%.3f' % (int(minutes) / 300)

                if Student.objects.filter(student_num__iexact=snum).exists():
                    student = Student.objects.get(student_num=int(snum))
                else:
                    logs.append(f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: "
                                "STUDENT NUMBER NOT FOUND")
                    continue

                if not student.last.lower() == last_name.lower():
                    logs.append(f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: "
                                "LAST NAME DOES NOT MATCH")
                    continue

                grade = student.grade_set.get(grade=int(student.homeroom[:2]))

                # create point type if missing
                try:
                    point_type = PointCodes.objects.filter(catagory=point_catagory).get(code=code)
                except PointCodes.DoesNotExist:
                    point_type = PointCodes(catagory=point_catagory, code=code, description=point_catagory + code)
                    point_type.save()

                grade.points_set.create(type=point_type, amount=points, entered_by=entered_by)
                logs.append(f"Success: {points} point(s) of {point_type.description} for {student.first} {student.last} was entered.")

    template = get_template('entry/submission-summary.html')
    context = {
        'logs': logs,
        'category': point_catagory,
    }
    return HttpResponse(template.render(context, request))


def validate_student_name(request):
    student_id = request.GET.get('student_id', None)
    student = Student.objects.filter(student_num__iexact=student_id)
    if student.exists():
        student = student[0]
        grade = student.grade_set.get(grade=int(student.homeroom[:2]))
        data = {
            'student_name': student.first + " " + student.last,
            't1': grade.scholar_set.all()[0].term1,
            't2': grade.scholar_set.all()[0].term2,
        }
    else:
        data = {
            'student_name': "Student not found",
            't1': '0',
            't2': '0',
        }
    return JsonResponse(data)


def validate_point_code(request):
    code_num = request.GET.get('code', None)
    category = request.GET.get('category', None)
    code = PointCodes.objects.filter(code__iexact=code_num, catagory__iexact=category)
    if code.exists():
        data = {
            'code_description': code[0].description,
        }
    else:
        data = {
            'code_description': "Code not found",
        }
    return JsonResponse(data)
