from django.contrib import admin
from .models import Configuration
from axes.admin import AccessAttemptAdmin, AccessLogAdmin
from axes.models import AccessAttempt, AccessLog

admin.site.unregister(AccessAttempt)
admin.site.unregister(AccessLog)


class MyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        obj.save(request.user)


admin.site.register(Configuration, MyAdmin)


@admin.register(AccessAttempt)
class MyAccessAttemptAdmin(AccessAttemptAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


@admin.register(AccessLog)
class MyAccessLogAdmin(AccessLogAdmin):
    def has_change_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
