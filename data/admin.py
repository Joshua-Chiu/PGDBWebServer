from django.contrib import admin
from import_export import resources
from .models import Student, PlistCutoff, Grade
from import_export.admin import ImportExportModelAdmin, ImportMixin
from django.dispatch import receiver
from import_export.signals import post_import, post_export
from import_export.formats import base_formats
from django.utils import timezone
from import_export.forms import ImportForm, ConfirmImportForm
import datetime
from django import forms
import csv
from django.http import HttpResponse, HttpResponseRedirect
from django.conf.urls import url, include
from django.template.loader import get_template
import re

admin.site.register(PlistCutoff)


def increase_grade(modeladmin, request, queryset):
    for student in queryset:
        new_grade = int(re.findall('\d+', student.homeroom)[0]) + 1
        student.homeroom = str(new_grade).zfill(2) + re.sub("\d+", "", student.homeroom)

        if new_grade > 12:
            pass  # mark inactive
        else:
            student.save()


increase_grade.short_description = 'Update Grade and Homerooms to New School Year '


def decrease_grade(modeladmin, request, queryset):
    for student in queryset:
        new_grade = int(re.findall('\d+', student.homeroom)[0]) - 1
        student.homeroom = str(new_grade).zfill(2) + re.sub("\d+", "", student.homeroom)

        if new_grade < 8:
            pass  # mark inactive
        else:
            student.grade_set.get(grade=new_grade + 1).delete()
            student.save()  # also delete oldest grade set


decrease_grade.short_description = 'Decrease Grade DATA LOSS POSSIBLE FOR THE HIGHEST GRADE'


def mark_inactive(modeladmin, request, queryset):
    pass


def export_as_csv(modeladmin, request, queryset):
    field_names = modeladmin.resource_class.Meta.fields
    file_name = "student_export_thing"  # TODO better name include date maybe

    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f"attachment; filename={file_name}.csv"
    writer = csv.writer(response, dialect="excel", lineterminator="\n")

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response


export_as_csv.short_description = "Export Selected as CSV"


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('student_num',)
        fields = ('first', 'last', 'legal', 'student_num', 'homeroom', 'sex', 'grad_year')
        export_order = ['student_num', 'first', 'last', 'legal', 'sex', 'homeroom', 'grad_year']


class StudentAdmin(admin.ModelAdmin):
    resource_class = StudentResource
    formats = (base_formats.XLSX, base_formats.ODS, base_formats.CSV, base_formats.CSV)
    list_display = ['last', 'first', 'legal', 'student_num', 'sex', 'homeroom']
    list_display_links = ('last', 'first')
    actions = [increase_grade, decrease_grade, export_as_csv, mark_inactive]
    search_fields = ('first', 'last', 'student_num',)

    def import_as_csv(self, request):
        if "file" in request.FILES:
            print("asdf")
            for line in request.FILES['file']:
                # if it's the start line skip it
                if line.decode("utf-8") == \
                        "first	last	legal	student_num	homeroom	sex	grad_year\n":
                    continue

                print(line.decode("utf-8").strip().split("\t"))
                first, last, legal, student_num, homeroom, sex, grad_year = line.decode("utf-8").strip().split("\t")
                # skip if student exists
                if Student.objects.filter(student_num=int(student_num)):
                    print(f"student {student_num} already exists")
                    # continue

                student = Student(first=first, last=last, legal=legal, student_num=student_num,
                                  homeroom=homeroom, sex=sex, grad_year=grad_year)
                student.save()

                # add grades
                for i in range(int(student.homeroom[:2]) - 7):
                    student.grade_set.create(grade=8 + i,
                                             start_year=timezone.now().year - int(student.homeroom[:2]) + 8 + i)
                    student.grade_set.get(grade=8 + i).scholar_set.create(term1=0, term2=0)

                student.save()

        template = get_template('admin/data/student/import.html')
        context = {
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title,
        }
        return HttpResponse(template.render(context, request))

    def get_urls(self):
        urls = super(StudentAdmin, self).get_urls()
        my_urls = [
            url(r"^import/$", self.import_as_csv)
        ]
        return my_urls + urls


admin.site.register(Student, StudentAdmin)


@receiver(post_import)
def _post_import(model, **kwargs):
    pass


@receiver(post_export)
def _post_export(model, **kwargs):
    # model is the actual model instance which after export
    pass


class DataAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        print(obj)
        super().save_model(request, obj, form, change)
