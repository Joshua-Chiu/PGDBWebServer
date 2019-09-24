from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    autofocus = models.IntegerField(default=1, choices=[(1, 'Service'), (2, 'Athletics'), (3, 'Fine Arts'), (4, 'Scholar T1'), (5, 'Scholar T2')])

    can_view = models.BooleanField(default=False, verbose_name='Can view student page',
                                help_text="Designates whether the user can see the student view.")

    no_entry = models.BooleanField(default=True, verbose_name='No entry at student page',
                                help_text="Designates whether the user can enter data at the student view.")


    def __str__(self):
        return self.first_name + " " + self.last_name


