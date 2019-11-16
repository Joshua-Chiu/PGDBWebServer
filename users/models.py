from django.contrib.auth.models import AbstractUser
from django.db import models
from django import template
from django.contrib.auth.models import Group

register = template.Library()


class CustomUser(AbstractUser):
    # Personalization Fields
    autofocus = models.IntegerField(default=1,
                                    choices=[(1, 'Service'), (2, 'Athletics'), (3, 'Fine Arts'), (4, 'Scholar T1'),
                                             (5, 'Scholar T2')])
    header_colour = models.CharField(max_length=7, default='#ADD8E6')
    page_colour = models.CharField(max_length=7, default='#ADD8E6')

    # Permission Booleans
    can_view = models.BooleanField(default=False, verbose_name='Can view student page with all information',
                                   help_text="Designates whether the user can see the student view with all the data. Note: If a user is a superuser, this is disregarded.")

    no_entry = models.BooleanField(default=True, verbose_name='Disable entry at student page',
                                   help_text="Designates whether the user can enter data at the student view. Note: If a user is a superuser, this is disregarded.")

    can_upload = models.BooleanField(default=False, verbose_name='Bulk upload at Direct Entry',
                                     help_text="Designates whether the user can submit files for at direct entry pages. Note: If a user is a superuser, this is disregarded.")

    @register.filter(name='has_group')
    def has_group(self, group_name):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return False

        return group in self.groups.all()

    def __str__(self):
        return self.first_name + " " + self.last_name
