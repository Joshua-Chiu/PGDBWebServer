from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    fieldsets = (
        ('', {'fields': ('username',)}),
        ('Personal Information', {'fields': ('first_name', 'last_name', 'email',)}),
        ('Password', {'fields': ('password',)}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_staff', 'no_entry', 'can_view', 'can_upload','groups')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)
