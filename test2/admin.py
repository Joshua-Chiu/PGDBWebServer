from django.contrib import admin
from import_export import resources
from .models import Student, PlistCutoff
from import_export.admin import ImportExportModelAdmin
from django.dispatch import receiver
from import_export.signals import post_import, post_export

# admin.site.register(Student)
admin.site.register(PlistCutoff)

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        import_id_fields = ('student_num')
        exclude = ('id')

class StudentAdmin(ImportExportModelAdmin):
    resource_class = StudentResource

admin.site.register(Student, StudentAdmin)

@receiver(post_import)
def _post_import(model, **kwargs):
    # model is the actual model instance which after import
    pass

@receiver(post_export)
def _post_export(model, **kwargs):
    # model is the actual model instance which after export
    pass
