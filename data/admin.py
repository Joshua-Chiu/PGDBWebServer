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
from django.http import HttpResponse

admin.site.register(PlistCutoff)


def increase_grade(modeladmin, request, queryset):
    for student in queryset:
        new_grade = int(student.homeroom[:-1])
        student.homeroom = str(new_grade).zfill(2) + student.homeroom[-1:]

        if new_grade > 12:
            pass  # mark inactive
        else:
            student.grade_set.create(grade=new_grade, start_year=timezone.now().year)
            student.grade_set.get(grade=new_grade).scholar_set.create(term1=0, term2=0)
            student.save()  # also create new grade set


def mark_inactive(modeladmin, request, queryset):
    pass


def export_as_tsv(modeladmin, request, queryset):
    field_names = modeladmin.resource_class.Meta.fields
    file_name = "student_export_thing" # TODO better name include date maybe

    response = HttpResponse(content_type='text/tsv')
    response['Content-Disposition'] = f'attachment; filename={file_name}.tsv'
    writer = csv.writer(response, dialect='excel-tab')

    writer.writerow(field_names)
    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_as_tsv.short_description = "Export selected as tsv"


increase_grade.short_description = 'Update Grade and Homerooms to New School Year '


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('student_num',)
        fields = ('first', 'last', 'legal', 'student_num', 'homeroom', 'sex', 'grad_year')
        export_order = ['student_num', 'first', 'last', 'legal', 'sex', 'homeroom', 'grad_year']


class StudentAdmin(admin.ModelAdmin):
    resource_class = StudentResource
    formats = (base_formats.XLSX, base_formats.ODS, base_formats.CSV, base_formats.TSV)
    list_display = ['last', 'first', 'legal', 'student_num', 'sex', 'homeroom']
    list_display_links = ('last', 'first')
    actions = [increase_grade, export_as_tsv, mark_inactive]


admin.site.register(Student, StudentAdmin)


@receiver(post_import)
def _post_import(model, **kwargs):
    print(model)
    print(kwargs)


@receiver(post_export)
def _post_export(model, **kwargs):
    # model is the actual model instance which after export
    pass
