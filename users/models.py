from django.contrib.auth.models import AbstractUser
from django.db import models
from django import template
from django.contrib.auth.models import Group

register = template.Library()


class AccessControl(models.Model):
    identifier = models.CharField(max_length=250, default='Set Identifier')
    description = models.CharField(max_length=250, default='Set Description')


class CustomUser(AbstractUser):
    # Personalization Fields
    autofocus = models.IntegerField(default=1,
                                    choices=[(1, 'Service'), (2, 'Athletics'), (3, 'Fine Arts'), (4, 'Scholar T1'),
                                             (5, 'Scholar T2')])
    first_visit = models.BooleanField(default=True)

    header_colour = models.CharField(max_length=7, default='#ADD8E6')
    page_colour = models.CharField(max_length=7, default='#ADD8E6')
    alternate_row_colour = models.CharField(max_length=7, default='#7AD7F0')
    text_colour = models.CharField(max_length=7, default='#000000')
    collapsible_bar_colour = models.CharField(max_length=7, default='#eeeeee')

    permissions = models.ManyToManyField(AccessControl)

    @property
    def can_upload(self):
        return True

    @property
    def no_entry(self):
        return False

    @property
    def can_view(self):
        return True

    @register.filter(name='has_group')
    def has_group(self, group_name):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return False

        return group in self.groups.all()

    def __str__(self):
        return self.first_name + " " + self.last_name
