from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import os, pytz
import datetime
# from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.loader import render_to_string, get_template
from django.urls import reverse
from axes.utils import reset

from accounts.views import daniel_lai
from util.roll_converter import roll_convert
from .models import Student, PointCodes, PlistCutoff, Points

from django.db import close_old_connections
import xml.etree.ElementTree as ET
import dateutil.parser
import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from axes.utils import reset

logs = []
done = False


def ajax_student_points_data(request):
    #  snum = request.GET.get('student_num', None)
    #  student = Student.objects.get(student_num=snum)
    data = {}
    return JsonResponse(data)


def ajax_student_cumulative_data(request):
    snum = request.GET.get('student_num', None)
    student = Student.objects.get(student_num=snum)
    grade = student.cur_grade_num
    data = {
        'silver': student.silver_pin,
        'gold': student.gold_pin,
        'goldplus': None,
        'platinum': None,
        'bigblock': student.bigblock_award,
        'TOTAL8': round(sum([student.cumulative_SE(8), student.cumulative_AT(8),
                              student.cumulative_SC(8), student.cumulative_FA(8)]), 2),
        'TOTAL9': round(sum([student.cumulative_SE(9), student.cumulative_AT(9),
                              student.cumulative_SC(9), student.cumulative_FA(9)]), 2),
        'TOTAL10': round(sum([student.cumulative_SE(10), student.cumulative_AT(10),
                              student.cumulative_SC(10), student.cumulative_FA(10)]), 2),
        'TOTAL11': round(sum([student.cumulative_SE(11), student.cumulative_AT(11),
                              student.cumulative_SC(11), student.cumulative_FA(11)]), 2),
        'TOTAL12': round(sum([student.cumulative_SE(12), student.cumulative_AT(12),
                              student.cumulative_SC(12), student.cumulative_FA(12)]), 2),
        'SE8': round(student.cumulative_SE(8), 2),
        'SE9': round(student.cumulative_SE(9), 2),
        'SE10': round(student.cumulative_SE(10), 2),
        'SE11': round(student.cumulative_SE(11), 2),
        'SE12': round(student.cumulative_SE(12), 2),
        'AT8': round(student.cumulative_AT(8), 2),
        'AT9': round(student.cumulative_AT(9), 2),
        'AT10': round(student.cumulative_AT(10), 2),
        'AT11': round(student.cumulative_AT(11), 2),
        'AT12': round(student.cumulative_AT(12), 2),
        'SC8': round(student.cumulative_SC(8), 2),
        'SC9': round(student.cumulative_SC(9), 2),
        'SC10': round(student.cumulative_SC(10), 2),
        'SC11': round(student.cumulative_SC(11), 2),
        'SC12': round(student.cumulative_SC(12), 2),
        'FA8': round(student.cumulative_FA(8), 2),
        'FA9': round(student.cumulative_FA(9), 2),
        'FA10': round(student.cumulative_FA(10), 2),
        'FA11': round(student.cumulative_FA(11), 2),
        'FA12': round(student.cumulative_FA(12), 2),
    }
    if grade >= 12:
        grad = {
            'platinum': student.platinum_pin,
            'gradAVG': float(round((student.grade_12.term1_avg + student.grade_12.term2_avg + student.grade_11.term1_avg + student.grade_11.term2_avg)/4, 2)),
            'gradSE': round(student.grade_12.SE_total + student.grade_11.SE_total, 2),
            'gradAT': round(student.grade_12.AT_total + student.grade_11.AT_total, 2),
            'gradSC': round(student.grade_12.SC_total + student.grade_11.SC_total, 2),
            'gradFA': round(student.grade_12.FA_total + student.grade_11.FA_total, 2),
            'gradTOTAL': round(
                sum([student.grade_12.SE_total + student.grade_11.SE_total, student.grade_12.AT_total + student.grade_11.AT_total, student.grade_12.SC_total + student.grade_11.SC_total, student.grade_12.FA_total + student.grade_11.FA_total]),
                2),
        }
        data.update(grad)
        data.update({'goldplus': student.goldPlus_pin, })
    elif grade >= 11:
        data.update({'goldplus': student.goldPlus_pin, })

    # add annual certificates to data dict
    for g in range(8, grade + 1):
        grade_object = student.get_grade(g)
        data['annual SE ' + str(g)] = grade_object.SE_total
        data['annual AT ' + str(g)] = grade_object.AT_total
        data['annual FA ' + str(g)] = grade_object.FA_total
        data['annual SC ' + str(g)] = grade_object.SC_total

        data['annual HR ' + str(g)] = grade_object.term1_avg >= 79.45 and grade_object.term2_avg >= 79.45
        try:
            data['annual PL ' + str(g)] = grade_object.term1_avg >= grade_object.plist_T1 and \
                                              grade_object.term2_avg >= grade_object.plist_T2
        except PlistCutoff.DoesNotExist:
            data['annual PL ' + str(g)] = False

    return JsonResponse(data)


def export_pgdb_archive(student_list, relevent_plists):
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
        for grade in student.all_grades():
            grade_tag = ET.SubElement(grades, 'grade')

            ET.SubElement(grade_tag, 'grade_num').text = str(grade.grade)
            ET.SubElement(grade_tag, 'start_year').text = str(grade.start_year)
            ET.SubElement(grade_tag, 'anecdote').text = str(grade.anecdote)

            ET.SubElement(grade_tag, 'AverageT1').text = str(grade.term2_avg)
            ET.SubElement(grade_tag, 'AverageT2').text = str(grade.term1_avg)

            points_tag = ET.SubElement(grade_tag, 'points')
            for point in grade.points_set.all():
                point_tag = ET.SubElement(points_tag, 'point')

                ET.SubElement(point_tag, 'catagory').text = str(point.type.catagory)
                ET.SubElement(point_tag, 'code').text = str(point.type.code)
                ET.SubElement(point_tag, 'amount').text = str(point.amount)

            # if a plist for this year exists add it to the list
            if grade.start_year not in relevent_plists and \
                    len(PlistCutoff.objects.filter(year=grade.start_year)) == 1:
                relevent_plists.append(grade.start_year)

    plists = ET.SubElement(root, "plists")
    for plist in relevent_plists:
        plist_object = PlistCutoff.objects.get(year=plist)
        plist_tag = ET.SubElement(plists, 'plist')

        ET.SubElement(plist_tag, 'year').text = str(plist)

        ET.SubElement(plist_tag, 'grade_8_T1').text = str(plist_object.grade_8_T1)
        ET.SubElement(plist_tag, 'grade_8_T2').text = str(plist_object.grade_8_T2)
        ET.SubElement(plist_tag, 'grade_9_T1').text = str(plist_object.grade_9_T1)
        ET.SubElement(plist_tag, 'grade_9_T2').text = str(plist_object.grade_9_T2)
        ET.SubElement(plist_tag, 'grade_10_T1').text = str(plist_object.grade_10_T1)
        ET.SubElement(plist_tag, 'grade_10_T2').text = str(plist_object.grade_10_T2)
        ET.SubElement(plist_tag, 'grade_11_T1').text = str(plist_object.grade_11_T1)
        ET.SubElement(plist_tag, 'grade_11_T2').text = str(plist_object.grade_11_T2)
        ET.SubElement(plist_tag, 'grade_12_T1').text = str(plist_object.grade_12_T1)
        ET.SubElement(plist_tag, 'grade_12_T2').text = str(plist_object.grade_12_T2)

    return root


def import_pgdb_file(tree):
    global logs
    global done
    logs = []
    done = False
    root = tree.getroot()
    # all students
    for s in root[0]:
        try:
            if len(Student.objects.filter(student_num=int(s[0].text))) != 0:
                print(f"Student with number {s[0].text} already exists")
                logs.append(f"Student with number {s[0].text} \t ({s[4].text}, {s[3].text}) already exists")
                continue

            s_obj = Student(
                student_num=int(s[0].text),
                cur_grade_num=int(s[1].text),
                homeroom_str=f"{s[2].text}",
                first=s[3].text,
                last=s[4].text,
                legal=s[5].text,
                sex=s[6].text,
                grad_year=int(s[7].text)
            )
            s_obj.save()

            for g in s[8]:

                g_obj = s_obj.get_grade(int(g[0].text))
                g_obj.anecdote = g[2].text or ""

                g_obj.term1_avg = float(g[3].text)
                g_obj.term2_avg = float(g[4].text)

                for p in g[5]:
                    if (len(PointCodes.objects.filter(catagory=p[0].text).filter(
                            code=int(p[1].text))) == 0):
                        type = PointCodes(catagory=p[0].text, code=int(p[1].text),
                                          description=str(p[0].text) + str(p[1].text))
                        type.save()
                    else:
                        type = PointCodes.objects.filter(catagory=p[0].text).get(code=int(p[1].text))

                    g_obj.add_point(Points(type=type, amount=float(p[2].text)))

                g_obj.calc_points_total("SE")
                g_obj.calc_points_total("AT")
                g_obj.calc_points_total("FA")
                g_obj.save()

            # logs.append(f"Added student {s[0].text} \t ({s[4].text}, {s[3].text}) successfully")
        except Exception as e:
            raise e
            return
            student_num = int(s[0].text)
            print(f"Failed to add student {int(s[0].text)}")
            logs.append(f"Failed to add student {s[0].text} \t ({s[4].text}, {s[3].text})")

            # delete the partially formed student
            if len(Student.objects.filter(student_num=student_num)) != 0:
                Student.objects.get(student_num=student_num).delete()

    for plist in root[1]:
        print(plist)

    done = True
    print(done)
    close_old_connections()


def ajax_import_status(request):
    if not done:
        data = {'done': 'false'}
        return JsonResponse(data)
    global logs
    data = {
        'logs': logs,
        'done': 'true'
    }

    return JsonResponse(data)


def show_all(request):
    template = get_template('data/all-points.html')
    context = {
    }
    return HttpResponse(template.render(context, request))


def ajax_all_points(request):
    data = []
    for point in Points.objects.all().order_by('-id'):
        try:
            entered_by = f"{point.entered_by.first} {point.entered_by.last}"
        except:
            entered_by = "Importer"
        data.append({
            'student': f"{point.get_student().first} {point.get_student().last}",
            'point': point.amount,
            'description': point.type.description,
            'grade': point.Grade.grade,
            'enteredby': entered_by,
        })
    return JsonResponse(data, safe=False)


def convert_roll(year, term, file):

    plist_cutoffs, students = roll_convert((l.decode() for l in file), ["YCPM", "YBMO", "YIPS", "MCE8", "MCE9", "MCLC"])

    plist = PlistCutoff.objects.get(year=year)
    for grade, cutoff in plist_cutoffs:
        print(plist, f"grade_{grade}_T{term}")
        setattr(plist, f"grade_{grade}_T{term}", cutoff)
        plist.save()

    for s in students:
        try:
            grade = Student.objects.get(student_num=s.number).get_grade(s.grade)
            if term == "1":
                grade.term1_avg = s.average
                grade.term1_GE = s.GE

            else:
                grade.term2_avg = s.average
                grade.term2_GE = s.GE
            grade.save()
        except:
            pass


def reset_users(request):
    reset(request.GET['username'])
    return HttpResponseRedirect(request.path)


def welcome(request):
    request.user.first_visit = True
    daniel_lai(request)
    request.user.save()
    reset(username=request.user.username)
    return HttpResponseRedirect(reverse('data:index'))
