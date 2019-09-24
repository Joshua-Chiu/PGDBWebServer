from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
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
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_staff', 'no_entry', 'can_view', 'groups')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )


admin.site.register(CustomUser, CustomUserAdmin)
