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


increase_grade.short_description = 'Update Grade and Homerooms to New School Year '


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('student_num',)
        fields = ('first', 'last', 'legal', 'student_num', 'homeroom', 'sex', 'grad_year')
        export_order = ['student_num', 'first', 'last', 'legal', 'sex', 'homeroom', 'grad_year']


class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource
    formats = (base_formats.XLSX, base_formats.ODS, base_formats.CSV, base_formats.TSV)
    list_display = ['last', 'first', 'legal', 'student_num', 'sex', 'homeroom']
    list_display_links = ('last', 'first')
    actions = [increase_grade, mark_inactive, ]


admin.site.register(Student, StudentAdmin)


@receiver(post_import)
def _post_import(model, **kwargs):
    # model is the actual model instance which after import
    pass


@receiver(post_export)
def _post_export(model, **kwargs):
    # model is the actual model instance which after export
    pass
