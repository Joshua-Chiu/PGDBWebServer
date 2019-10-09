from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template.loader import get_template
from data.models import Student, PointCodes, Points
from django.http import JsonResponse
from data.views import google_calendar


def checkUser(user, category):
    return user.groups.filter(name=category).exists() or user.is_superuser


def index(request):
    maintenance, notice = google_calendar()
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
    if request.user.is_authenticated and checkUser(request.user, "Service"):
        template = get_template('entry/service.html')
        context = {
            'points': Points.objects.filter(entered_by=request.user, type__catagory='SE').order_by('-id')
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def athletics(request):
    if request.user.is_authenticated and checkUser(request.user, "Athletics"):
        template = get_template('entry/athletics.html')
        context = {
            'points': Points.objects.filter(entered_by=request.user, type__catagory='AT').order_by('-id')
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('error')


def fine_arts(request):
    if request.user.is_authenticated and checkUser(request.user, "Fine Arts"):
        template = get_template('entry/fine-arts.html')
        context = {
            'points': Points.objects.filter(entered_by=request.user, type__catagory='FA').order_by('-id')
        }
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


def scholar_submit(request):
    if request.method == "POST":
        try:
            snum = int(request.POST["student-number"])
            term1 = float(request.POST["t1"])
            term2 = float(request.POST["t2"])

            student = Student.objects.get(student_num=snum)
            grade = student.grade_set.get(grade=int(student.homeroom[:2]))

            scholar = grade.scholar_set.all()[0]
            scholar.term1 = term1
            scholar.term2 = term2
            scholar.save()
        except Exception as e:
            print(e)
            print("failed to submit scholar")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


def scholar_upload_file(request):
    error_msgs = []
    entered_by = request.user
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

                grade = student.grade_set.get(grade=int(student.homeroom[:2]))

                grade.scholar_set.objects.all()[0].term1 = term1
                grade.scholar_set.objects.all()[0].term2 = term2

                error_msgs.append(
                    f"Success: added term 1 and 2 averages for {student.first} {student.last} was "
                    "entered.")

    context = {}
    return HttpResponseRedirect("/entry/scholar")


def error(request):
    template = get_template('entry/error.html')
    context = {}
    if request.user.is_authenticated:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/data')


@login_required
def dictionary(request, point_catagory):
    template = get_template('entry/dictionary.html')
    context = {
        'codes': PointCodes.objects.filter(catagory=point_catagory)
    }
    return HttpResponse(template.render(context, request))


def point_submit(request, point_catagory):
    if request.method == "POST":
        try:
            snum = int(request.POST["student-number"])
            code = int(request.POST["code"])
            points = int(request.POST["minutes"])
            if point_catagory == "SE":
                points /= 300

            student = Student.objects.get(student_num=snum)
            grade = student.grade_set.get(grade=int(student.homeroom[:2]))
            grade.points_set.create(
                type=PointCodes.objects.filter(catagory=point_catagory).get(code=code),
                amount=points,
                entered_by=request.user,
            )
        except Exception as e:
            print(e)
            print("failed to submit")

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def upload_file(request, point_catagory):
    error_msgs = []
    entered_by = request.user
    if request.method == "POST":
        if "file" in request.FILES:
            for line in request.FILES['file']:
                # if it's the start line skip it
                if line.decode("utf-8") == "Student Number,Last Name,Minutes of Service,Code\n":
                    if point_catagory == "SE":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break
                if line.decode("utf-8") == "Student Number,Last Name,Athletic Points,Code\n":
                    if point_catagory == "AT":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break
                if line.decode("utf-8") == "Student Number,Last Name,Fine Art Points,Code\n":
                    if point_catagory == "FA":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break
                if line.decode("utf-8") == "Student Number,Last Name,Average T1,Average T2\n":
                    if point_catagory == "FA":
                        continue
                    else:
                        error_msgs.append("Error: File submitted at wrong entry point.")
                        break

                if line.decode("utf-8") == ",,,\n":  # skip blank lines
                    continue

                # print(line.decode("utf-8").strip())
                print(line.decode("utf-8").strip().split(","))
                snum, last_name, minutes, code = line.decode("utf-8").strip().split(",")[:4]

                points = float(minutes)
                if point_catagory == "SE":  # divide by 300 only if it's SE
                    points = '%.3f' % (int(minutes) / 300)
                if point_catagory == "AT" and points > 6:  # check less than 6 for AT
                    error_msgs.append(
                        f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: "
                        "POINTS EXCEEDED MAXIMUM VALUE")
                    continue
                if point_catagory == "FA" and points > 10:  # check less than 10 for FA
                    error_msgs.append(
                        f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: "
                        "POINTS EXCEEDED MAXIMUM VALUE")
                    continue

                if Student.objects.filter(student_num__iexact=snum).exists():
                    student = Student.objects.get(student_num=int(snum))
                else:
                    error_msgs.append(f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: "
                                "STUDENT NUMBER NOT FOUND")
                    continue

                if not student.last.lower() == last_name.lower():
                    error_msgs.append(f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: "
                                "LAST NAME MISMATCH")
                    continue

                grade = student.grade_set.get(grade=int(student.homeroom[:2]))

                # create point type if missing
                if PointCodes.objects.filter(catagory=point_catagory).filter(code=code).exists():
                    point_type = PointCodes.objects.filter(catagory=point_catagory).get(code=code)
                else:
                    error_msgs.append(f"Error: {points} point(s) of Code {point_catagory}{code} for {snum} was not entered: "
                                "CODE UNDEFINED")
                    continue

                grade.points_set.create(type=point_type, amount=points, entered_by=entered_by)
                error_msgs.append(
                    f"Success: {points} point(s) of {point_type.description} for {student.first} {student.last} was "
                    "entered.")

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
        grade = student.grade_set.get(grade=int(student.homeroom[:2]))
        data = {
            'student_name': student.first + " " + student.last,
            't1': round(grade.scholar_set.all()[0].term1, 3),
            't2': round(grade.scholar_set.all()[0].term2, 3),
        }
    else:
        data = {
            'student_name': "Student not found",
            't1': '0',
            't2': '0',
        }
    return JsonResponse(data)


def validate_point_code(request):
    code_num = int(request.GET.get('code', None))
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
