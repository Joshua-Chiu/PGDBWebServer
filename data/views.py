from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from .models import Student, PointCodes,  PlistCutoff
from users.models import CustomUser
from django.template.loader import get_template
from itertools import zip_longest
import datetime
import io
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from util.queryParse import parseQuery
from django.contrib.auth.decorators import login_required


@login_required()
def search(request):
    template = get_template('data/search.html')
    
    # if no query exists make an empty list
    if request.GET['query']:
        query = request.GET['query']
    else:
        return HttpResponse(template.render(None, request))

    students = parseQuery(query)

    if len(students) == 1:
        return HttpResponseRedirect(f"/data/student/{students[0].id}")
    context = {
        'student_list': students,
        'query': request.GET['query']
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def student_info(request, num):
    template = get_template('data/student_info.html')
    context = {
        'student': Student.objects.get(id=num),
        'plists': PlistCutoff.objects.all()
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


@login_required
def student_submit(request, num):
    student = Student.objects.get(id=num)
    items = list(request.POST.items())[1:]
    anecdotes = [item for item in items if item[0].find("anecdote") != -1]
    points_list = [item for item in items if item[0].find("points") != -1 or item[0].find("code") != -1]
    scholar_fields = [item for item in items if item[0].find("SC") != -1]
    points_list = points_list + scholar_fields
    code_delete_buttons = [item for item in items if item[0].find("deletePoint") != -1]

    # anecdotes
    for n, anecdote in enumerate(anecdotes):
        # print(anecdote[1])
        grade = student.grade_set.get(grade=int(student.homeroom[:2])-n)
        grade.anecdote = anecdote[1]
        grade.save()

    # delete codes buttons
    for button in code_delete_buttons:
        # buttons are ['deletepoint <grade> <catagory> <code> ', 'X']
        grade, catagory, code = button[0].strip().split(' ')[1:]
        point = student.grade_set.get(grade=int(grade)).points_set.filter(type__catagory=catagory).filter(type__code=code)[0]
        point.delete()
        # print(point)
        # print("button: ", grade, type, code)

    # points and codes
    if request.method == 'POST':
        # print("received POST request")
        # for k, v in request.POST.items():
        #     print(k, "|", v)

        # iterate through pairs of point amount and code
        for point_field, code_field in zip(points_list[::2], points_list[1::2]):

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

                # set the scholar average
                grade = student.grade_set.get(grade=grade_num)
                scholar = grade.scholar_set.all()[0]
                scholar.term1 = t1
                scholar.term2 = t2
                scholar.save()
            else:
                if point_field[1] == '' or code_field[1] == '':
                    continue

                amount = float(point_field[1])
                code = int(code_field[1])

                # find the point class with the same code and catagory 
                try:
                    typeClass = PointCodes.objects.filter(catagory=type).get(code=code)
                except PointCodes.DoesNotExist as e:
                    typeClass = PointCodes(catagory=type, code=code, description="")
                    typeClass.save()

                grade = student.grade_set.get(grade=grade_num)
                grade.points_set.create(type=typeClass, amount=amount)

    return HttpResponseRedirect("/data/student/{}".format(num))


def archive(request):
    template = get_template('data/archive.html')
    context = {}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def archive_submit(request):
        return HttpResponseRedirect('/data/archive')

def archive_file(request):
    if not "query" in request.POST:
        raise Http404
    query = request.POST['query']

    print(f"query={query}")

    # fileType = request.GET['filetype']

    student_list = parseQuery(query)

    # xml_file = io.StringIO("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>")

    relevent_plists = []

    root = ET.Element('PGDB')

    students = ET.SubElement(root, "students")
    for student in student_list:
        student_tag = ET.SubElement(students, 'student')
        ET.SubElement(student_tag, 'number').text = str(student.student_num)
        ET.SubElement(student_tag, 'current_grade').text = str(student.homeroom[:-1])
        ET.SubElement(student_tag, 'homeroom').text = str(student.homeroom[-1:])
        ET.SubElement(student_tag, 'first').text = student.first
        ET.SubElement(student_tag, 'last').text = student.last
        ET.SubElement(student_tag, 'legal_name').text = student.legal
        ET.SubElement(student_tag, 'sex').text = student.sex
        ET.SubElement(student_tag, 'grad_year').text = str(student.grad_year)

        grades = ET.SubElement(student_tag, 'grades')
        for grade in student.grade_set.all():
            grade_tag = ET.SubElement(grades, 'grade')

            ET.SubElement(grade_tag, 'grade_num').text = str(grade.grade)
            ET.SubElement(grade_tag, 'start_year').text = str(grade.start_year)
            ET.SubElement(grade_tag, 'anecdote').text = str(grade.anecdote)

            if grade.start_year not in relevent_plists and \
                    len(PlistCutoff.objects.filter(year=grade.start_year)) == 1:
                        relevent_plists.append(grade.start_year)

    print(relevent_plists)

    plists = ET.SubElement(root, "plists")
    for plist in relevent_plists:
        plist_tag = ET.SubElement(plists, 'plist')

        ET.SubElement(plist_tag, 'year').text = str(plist)

    xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    xml_file = io.StringIO(xml_str)

    response = HttpResponse(xml_file, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=students.pgdb'

    return response


def settings(request):
    template = get_template('data/settings.html')
    context = {
    }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def codes(request):
    template = get_template('data/codes.html')
    context = {'codes': PointCodes.objects.order_by("catagory")}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def plist(request):
    template = get_template('data/plist.html')
    context = {
            'plist' : PlistCutoff.objects.all(),
            'year': datetime.datetime.now().year,
            'month': datetime.datetime.now().month
            }
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')


def plist_submit(request):
    plist = PlistCutoff.objects.all()
    items = request.POST

    for year in plist:
        year.grade_8_T1 = items[str(year.year) + " 8 1"]
        year.grade_8_T2 = items[str(year.year) + " 8 2"]

        year.grade_9_T1 = items[str(year.year) + " 9 1"]
        year.grade_9_T2 = items[str(year.year) + " 9 2"]

        year.grade_10_T1 = items[str(year.year) + " 10 1"]
        year.grade_10_T2 = items[str(year.year) + " 10 2"]

        year.grade_11_T1 = items[str(year.year) + " 11 1"]
        year.grade_11_T2 = items[str(year.year) + " 11 2"]

        year.grade_12_T1 = items[str(year.year) + " 12 1"]
        year.grade_12_T2 = items[str(year.year) + " 12 2"]

        year.save()

    return HttpResponseRedirect("/data/settings/plist")


def autofocus_submit(request, num):
    user = CustomUser.objects.all()[0]

    user.autofocus = num
    user.save()

    return HttpResponseRedirect("/data")


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
        filter_codes = filter_codes.filter(catagory=code[0][1])
        if len(filter_codes) == 1:
            entry = filter_codes[0]
        elif len(filter_codes) == 0:
            entry = PointCodes()
        else:
            print("panic!!")

        entry.code = code[1][1]
        entry.catagory = code[0][1].upper()
        entry.description = code[2][1]
        entry.save()

    return HttpResponseRedirect("/data/settings/codes")


def index(request):
    template = get_template('data/index.html')
    context = {
        'student_list': Student.objects.all()
    }

    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    elif request.user.is_authenticated:
        return HttpResponseRedirect('/entry')
    else:
        return HttpResponseRedirect('/')


def help(request):
    template = get_template('data/help.html')
    context = {}
    if request.user.is_superuser:
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponseRedirect('/')
