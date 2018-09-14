from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Student, PointCodes
from django.template.loader import get_template
from itertools import zip_longest

def search(request):
    template = get_template('test2/search.html')
    students = Student.objects.all()
    
    #if no query exists make an empty list
    if request.GET['query']:
        query = request.GET['query']
    else:
        return HttpResponse(template.render(None, request))

    # checl if there are attribute specifics e.g. first: bob
    if query.count(":") == 0:
        # search first and last if it's letters
        if query.isalpha():
            first = set(Student.objects.filter(first__icontains=query))
            last = set(Student.objects.filter(last__icontains=query))
            students = list(first.union(last))
        # else search student number
        elif query.isdigit():
            students = students.filter(student_num=query)
    else:
        query = query.replace(": ", ":")
        items = {}
        # split by spaces into attributes
        for i in query.split(' '):
            term = i.split(':')
            if len(term) != 2:
                continue
            items[term[0]] = term[1]

        # if it's an attribute of student filter by it
        for k, v in items.items():
            if hasattr(Student, k):
                val = "{0}__icontains".format(k)
                print(val, v)
                students = students.filter(**{val: v})
            else:
                # pretend there is a grade attribute
                if k == 'grade':
                    if len(v) == 1:
                        v = '0' + v
                    print('homeroom__contains', v)
                    students = students.filter(**{'homeroom__contains': v})
    # if one student is returned redirect to its page
    if len(students) == 1:
        return HttpResponseRedirect(f"/test2/student/{students[0].id}")
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
    student = Student.objects.get(id=num)
    items = list(request.POST.items())[1:]

    if request.method == 'POST':
        print("received POST request")
        for k, v in request.POST.items():
            print(k, "|", v)

        # iterate through pairs of point amount and code
        for point_field, code_field in zip(items[::2], items[1::2]):

            # get info like grade and point type e.g. SE, AT
            info = point_field[0].split(' ')
            grade_num = int(info[0])
            type = info[1]

            # decide if it's scholar or other type
            if type == "SC":
                # scholar gets its own class from the other points
                if point_field[1] == '' and code_field[1] == '':
                    continue

                if point_field[1] == '': t1 = 0
                else: t1 = float(point_field[1])

                if code_field[1] == '': t2 = 0
                else: t2 = float(code_field[1])

                grade = student.grade_set.get(grade=grade_num)
                grade.scholar_set.create(term1=t1, term2=t2)
            else:
                if point_field[1] == '' or code_field[1] == '':
                    continue

                amount = float(point_field[1])
                code = int(code_field[1])

                grade = student.grade_set.get(grade=grade_num)
                grade.points_set.create(code=code, type=type, amount=amount)

    return HttpResponseRedirect("/test2/student/{}".format(num))


def settings(request):
    template = get_template('test2/settings.html')
    context = {
    }
    return HttpResponse(template.render(context, request))


def codes(request):
    template = get_template('test2/codes.html')
    context = {'codes': PointCodes.objects.order_by("type")}
    return HttpResponse(template.render(context, request))


def codes_submit(request):

    # sort the codes into a list where each code is an item
    items = list(request.POST.items())[1:]
    args = [iter(items)] * 3
    code_info = list(zip_longest(*args))

    for code in code_info:
        if (not code[0][1]) or (not code [1][1]):
            continue

        # if there is an already existing code don't create a new one
        filter_codes = PointCodes.objects.filter(code=int(code[1][1]))
        filter_codes = filter_codes.filter(type=code[0][1])
        if len(filter_codes) == 1:
            entry = filter_codes[0]
        elif len(filter_codes) == 0:
            entry = PointCodes()
        else:
            print("panic!!")

        entry.code = code[1][1]
        entry.type = code[0][1].upper()
        entry.description = code[2][1]
        entry.save()

    return HttpResponseRedirect("/test2/settings/codes")


def student_list(request):
    template = get_template('test2/student_list.html')
    context = {
        'student_list': Student.objects.all()
    }
    return HttpResponse(template.render(context, request))


def index(request):
    template = get_template('test2/index.html')
    context = {
        'student_list': Student.objects.all()
    }
    return HttpResponse(template.render(context, request))


