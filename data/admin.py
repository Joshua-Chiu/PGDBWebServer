from django.contrib import admin
from import_export import resources
from .models import Student, PlistCutoff, Grade, LoggedAction
from import_export.admin import ImportExportModelAdmin, ImportMixin
from django.dispatch import receiver
from import_export.signals import post_import, post_export
from import_export.formats import base_formats
from django.utils import timezone
from import_export.forms import ImportForm, ConfirmImportForm
import datetime
from django import forms
import csv, re
from django.http import HttpResponse, HttpResponseRedirect
from django.conf.urls import url, include
from django.template.loader import get_template
import re
import threading


def increase_grade(modeladmin, request, queryset):
    def increase():
        for student in queryset:
            if student.cur_grade_num >= 12:
                student.active = False
                student.save()
            else:
                student.active = True
                student.cur_grade_num += 1
                student.save()

    thread = threading.Thread(target=increase)
    thread.start()


def decrease_grade(modeladmin, request, queryset):
    def decrease():
        for student in queryset:
            if student.cur_grade_num <= 8:
                student.active = False
                student.save()
            else:
                student.active = True
                student.cur_grade_num -= 1
                student.save()

    thread = threading.Thread(target=decrease)
    thread.start()


def mark_inactive(modeladmin, request, queryset):
    def inactive():
        for student in queryset:
            student.active = False
            student.save()

    thread = threading.Thread(target=inactive)
    thread.start()


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


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('student_num',)
        fields = ('first', 'last', 'legal', 'student_num', 'homeroom', 'sex', 'grad_year')
        export_order = ['student_num', 'first', 'last', 'legal', 'sex', 'homeroom', 'grad_year']


class StudentAdmin(admin.ModelAdmin):
    resource_class = StudentResource
    formats = (base_formats.XLSX, base_formats.ODS, base_formats.CSV, base_formats.CSV)
    list_display = ['last', 'first', 'legal', 'student_num', 'sex', 'homeroom', 'active']
    list_display_links = ('last', 'first')
    search_fields = ('first', 'last', 'student_num',)
    fieldsets = (
        ('Personal Information', {'fields': (
            'first',
            'last',
            'legal',
            'sex',
            'student_num',)}),
        ('Grade', {'fields': (
            'grad_year',
            'cur_grade_num',
            'homeroom_str')}),
        ('Status', {'fields': ('active',)}),
    )

    def get_actions(self, request):
        actions = super(StudentAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for s in queryset:
            s.delete()

    really_delete_selected.short_description = "Delete selected entries"


    def import_csv_file(self, file):
        for line in file:
            # if it's the start line skip it
            if line.decode("utf-8") == \
                    "Student Number,Last Name,First Name,Legal Name,Gender,Homeroom,Year of Graduation\n":
                continue

            print(line.decode("utf-8").strip().split("\t"))
            student_num, last, first, legal, sex, homeroom, grad_year = line.decode("utf-8").strip().split(",")
            # skip if student exists
            if Student.objects.filter(student_num=int(student_num)):
                print(f"student {student_num} already exists")
                continue

            try:
                student = Student(first=first, last=last, legal=legal, student_num=int(student_num),
                                  cur_grade_num=int(re.sub('\D', '', homeroom)),
                                  homeroom_str=homeroom.lstrip('0123456789'), sex=sex, grad_year=int(grad_year))
                student.save()
            except Exception as e:
                print(e)

    def import_as_csv(self, request):
        if "file" in request.FILES:
            thread = threading.Thread(target=self.import_csv_file, args=(request.FILES['file'], ))
            thread.start()
            template = get_template('data/file_upload.html')
            context = {}
            return HttpResponse(template.render(context, request))

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

    actions = [increase_grade, decrease_grade, export_as_csv, mark_inactive, really_delete_selected]


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


admin.site.register(PlistCutoff)
admin.site.register(LoggedAction)
increase_grade.short_description = 'Update Grade and Homerooms to New School Year '
decrease_grade.short_description = 'Decrease Grade'
export_as_csv.short_description = "Export Selected as CSV"
admin.site.register(Student, StudentAdmin)
