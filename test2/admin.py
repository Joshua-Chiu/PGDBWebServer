from django.contrib import admin
from import_export import resources
from .models import Student, PlistCutoff
from import_export.admin import ImportExportModelAdmin
from django.dispatch import receiver
from import_export.signals import post_import, post_export
from import_export.formats import base_formats
# admin.site.register(Student)
admin.site.register(PlistCutoff)


class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('student_num',)
        fields = ('first', 'last', 'legal', 'student_num', 'homeroom', 'sex')
        export_order = ['student_num', 'first', 'last', 'legal', 'sex']


class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource

    def get_export_formats(self):
        formats = (
            base_formats.CSV,
            base_formats.TSV,
            base_formats.XLSX,
            base_formats.ODS,
        )
        return [f for f in formats if f().can_export()]


    def get_import_formats(self):
        formats = (
            base_formats.CSV,
            base_formats.TSV,
            base_formats.XLSX,
            base_formats.ODS,
        )
        return [f for f in formats if f().can_export()]


admin.site.register(Student, StudentAdmin)


@receiver(post_import)
def _post_import(model, **kwargs):
    # model is the actual model instance which after import
    pass


@receiver(post_export)
def _post_export(model, **kwargs):
    # model is the actual model instance which after export
    pass
