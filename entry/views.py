from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from django.urls import reverse
import re
from data.models import Student, PointCodes, Points
from django.http import JsonResponse
from data.views import google_calendar

offline = False


def checkUser(user, category):
    global offline
    return (user.groups.filter(name=category).exists() and not offline) or user.is_superuser


def index(request):
    global offline
    maintenance, notice, offline = google_calendar()
    if offline and not request.user.is_superuser:
        return HttpResponseRedirect(reverse('configuration:offline'))
    template = get_template('entry/index.html')
    context = {
        'maintenance': maintenance,
        'notice': notice,
        'recent': Points.objects.filter(entered_by=request.user).order_by('-id')[:50]
    }
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def service(request):
    if checkUser(request.user, "Service"):
        template = get_template('entry/service.html')
        context = {
            'points': Points.objects.filter(entered_by=request.user, type__catagory='SE').order_by('-id')[:75]
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def athletics(request):
    if checkUser(request.user, "Athletics"):
        template = get_template('entry/athletics.html')
        context = {
            'points': Points.objects.filter(entered_by=request.user, type__catagory='AT').order_by('-id')[:75]
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def fine_arts(request):
    if checkUser(request.user, "Fine Arts"):
        template = get_template('entry/fine-arts.html')
        context = {
            'points': Points.objects.filter(entered_by=request.user, type__catagory='FA').order_by('-id')[:75]
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def scholar(request):
    if checkUser(request.user, "Scholar"):
        template = get_template('entry/scholar.html')
        context = {}
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def scholar_submit(request):
    if request.method == "POST":
        try:
            snum = int(request.POST["student-number"])
            term1 = float(request.POST["t1"])
            term2 = float(request.POST["t2"])

            student = Student.objects.get(student_num=snum)
            grade = student.get_grade(student.cur_grade_num)

            grade.term1_avg=term1
            grade.term2_avg=term2
            grade.save()
        except Exception as e:
            print(e)
            print("failed to submit scholar")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def scholar_upload_file(request):
    error_msgs = []
    if request.method == "POST":
        if "file" in request.FILES:
            for line in request.FILES['file']:
                if line.decode("utf-8") == ",,,\n":  # skip blank lines
                    continue

                snum, last_name, term1, term2 = line.decode("utf-8").strip().split(",")[:4]

                # if it's the start line skip it
                if snum == "Student Number" and last_name == "Last Name":
                    if term1 == "Average T1" and term2 == "Average T2":
                        continue
                    else:
                        return HttpResponseRedirect("/entry/scholar")

                if Student.objects.filter(student_num__iexact=snum).exists():
                    student = Student.objects.get(student_num=int(snum))
                else:
                    error_msgs.append(f"STUDENT NUMBER NOT FOUND")
                    continue

                if not student.last.lower() == last_name.lower():
                    error_msgs.append(f"Error: LAST NAME MISMATCH")
                    continue

                grade = student.get_grade(student.cur_grade_num)

                grade.term1_avg(term1)
                grade.term2_avg(term2)
                grade.save()

                error_msgs.append(
                    f"Success: added term 1 and 2 averages for {student.first} {student.last} was "
                    "entered.")

    context = {}
    return HttpResponseRedirect("/entry/scholar")


def error(request):
    template = get_template('entry/error.html')
    context = {}
    return HttpResponse(template.render(context, request))


def dictionary(request, point_catagory):
    template = get_template('entry/dictionary.html')
    context = {
        'codes': PointCodes.objects.filter(catagory=point_catagory)
    }
    return HttpResponse(template.render(context, request))


def point_submit(request, point_catagory):
    if request.method == "POST":
        try:
            if any(key.startswith("deletePoint ") for key in request.POST):
                for key in request.POST:
                    if key != 'csrfmiddlewaretoken':
                        Points.objects.get(id=int(key.replace("deletePoint ", ""))).delete(request.user)
            else:
                snum = int(request.POST["student-number"])
                code = int(request.POST["code"])
                points = float(request.POST["minutes"])
                if point_catagory == "SE":
                    points /= 5

                student = Student.objects.get(student_num=snum)
                grade = student.get_grade(student.cur_grade_num)
                grade.add_point(Points(
                    type=PointCodes.objects.filter(catagory=point_catagory).get(code=code),
                    amount=points,
                    entered_by=request.user),
                    request.user
                )
        except Exception as e:
            print(e)
            print("failed to submit")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def upload_file(request, point_catagory):
    error_msgs = []
    entered_by = request.user
    if request.method == "POST":
        if "file" in request.FILES:
            for line in request.FILES['file']:
                # if it's the start line skip it
                if "Student Number,Last Name,Minutes of Service,Code" in line.decode("utf-8"):
                    if point_catagory == "SE":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break
                if "Student Number,Last Name,Athletic Points,Code" in line.decode("utf-8"):
                    if point_catagory == "AT":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break
                if "Student Number,Last Name,Fine Art Points,Code" in line.decode("utf-8"):
                    if point_catagory == "FA":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break
                if "Student Number,Last Name,Average T1,Average T2" in line.decode("utf-8"):
                    if point_catagory == "FA":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break

                if line.decode("utf-8") == ",,,\n":  # skip blank lines
                    continue

                # print(line.decode("utf-8").strip())
                # print(line.decode("utf-8").strip().split(","))
                snum, last_name, minutes, code = line.decode("utf-8").strip().split(",")[:4]

                points = float(minutes)
                if int(snum) == 1234567:  # skip aardvark
                    continue
                if point_catagory == "SE":  # divide by 300 only if it's SE
                    points = '%.3f' % (int(minutes) / 300)

                if Student.objects.filter(student_num__iexact=snum).exists():
                    student = Student.objects.get(student_num=int(snum))
                else:
                    error_msgs.append(f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: STUDENT NUMBER NOT FOUND")
                    continue

                if PointCodes.objects.filter(catagory=point_catagory).filter(code=code).exists():
                    point_type = PointCodes.objects.filter(catagory=point_catagory).get(code=code)
                else:
                    error_msgs.append(f"Error: {points} point(s) of Code Type {point_catagory}{code} for {student.first} {student.last} ({student.student_num}) was not entered: CODE UNDEFINED")
                    continue

                if not student.last.lower() == last_name.lower():
                    error_msgs.append(
                        f"Error: {points} point(s) of Code Type ({point_catagory}{code}) {point_type.description} for {student.first} {student.last} ({student.student_num}) was not entered: LAST NAME MISMATCH")
                    continue

                if point_catagory == "AT" and points > 6:  # check less than 6 for AT
                    error_msgs.append(
                        f"Error: {points} point(s) of Code Type ({point_catagory}{code}) {point_type.description} for {student.first} {student.last} "
                        f"({student.student_num}) was not entered: POINTS EXCEEDED MAXIMUM VALUE OF 6")
                    continue
                if point_catagory == "FA" and points > 10:  # check less than 10 for FA
                    error_msgs.append(
                        f"Error: {points} point(s) of Code Type ({point_catagory}{code}) {point_type.description} for {student.first} {student.last} "
                        f"({student.student_num}) was not entered: POINTS EXCEEDED MAXIMUM VALUE OF 10")
                    continue

                grade = student.get_grade(student.cur_grade_num)
                grade.points_set.create(type=point_type, amount=points, entered_by=entered_by)
                error_msgs.append(
                    f"Success: {points} point(s) of Code Type ({point_catagory}{code}) {point_type.description} for {student.first} {student.last} ({student.student_num}) was entered.")

    template = get_template('entry/submission-summary.html')
    context = {
        'logs': error_msgs,
        'category': point_catagory,
    }
    return HttpResponse(template.render(context, request))


def validate_student_name(request):
    student_id = request.GET.get('student_id', None)
    student = Student.objects.filter(student_num__iexact=student_id)
    if student.exists():
        student = student[0]
        grade = student.cur_grade
        data = {
            'student_name': student.first + " " + student.last,
            't1': round(grade.term1_avg, 3),
            't2': round(grade.term2_avg, 3),
        }
    else:
        data = {
            'student_name': "Student not found",
            # 't1': '0',
            # 't2': '0',
        }
    return JsonResponse(data)


def validate_point_code(request):
    code_num = request.GET.get('code', None)
    category = request.GET.get('category', None)
    data = {
        'code_description': "Code not found",
    }
    if code_num:
        code = PointCodes.objects.filter(code__iexact=int(code_num), catagory__iexact=category)
        if code.exists():
            data = {
                'code_description': code[0].description,
            }
    return JsonResponse(data)
