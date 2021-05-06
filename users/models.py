from django.contrib.auth.models import AbstractUser
from django.db import models
from django import template
from django.contrib.auth.models import Group

register = template.Library()


class AccessControl(models.Model):
    identifier = models.CharField(max_length=250, default='Set Identifier', unique=True)
    description = models.CharField(max_length=250, default='Set Description')

    def __str__(self):
        return self.description


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

    accesscontrol = models.ManyToManyField(AccessControl,
        verbose_name=('Database Access Control'),
        blank=True,
        help_text=('Specify access control for this user. Ctrl + A to select all.'),
        related_name="accesscontrol_set",
        related_query_name="accesscontrol",)

    @register.filter(name='has_access')
    def has_access(self, perm):
        try:
            perm = AccessControl.objects.get(identifier=perm)
        except Exception as e:
            print(f"Can't find permission: {perm}")
            return False

        return perm in self.accesscontrol.all()

    @property
    def can_upload(self):
        return self.has_access("can_upload")

    @property
    def no_entry(self):
        return not self.has_access("can_enter")

    @property
    def can_view(self):
        return self.has_access("can_view")

    @register.filter(name='has_group')
    def has_group(self, group_name):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return False

        return group in self.groups.all()

    def __str__(self):
        return self.first_name + " " + self.last_name
